import io
import threading
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import func, select

from app.config import get_settings
from app.core import deps
from app.db import SessionLocal
from app.main import app
from app.models import Asset, AssetAssignment, Notification
from app.schemas.common import validate_form
from app.schemas.forms import CheckinForm, CheckoutForm
from app.services import assignments
from app.services.common import FormError
from app.services.warranty import run_warranty_job
from tests.conftest import PASSWORD, asset_data


def test_login_and_idle_timeout(admin, monkeypatch):
    c = TestClient(app, follow_redirects=False)
    bad = c.post("/login", data={"email": "admin@example.com", "password": "wrong"})
    assert bad.status_code == 401
    ok = c.post("/login", data={"email": "admin@example.com", "password": PASSWORD})
    assert ok.status_code == 303
    assert c.get("/assets").status_code == 200

    real = deps._now
    monkeypatch.setattr(deps, "_now", lambda: real() + 31 * 60)
    expired = c.get("/assets")
    assert expired.status_code == 303 and "/login" in expired.headers["location"]
    monkeypatch.setattr(deps, "_now", real)
    assert c.get("/assets").status_code == 303  # session was cleared


def test_unauthenticated_htmx_gets_hx_redirect():
    c = TestClient(app, follow_redirects=False)
    r = c.get("/assets", headers={"HX-Request": "true"})
    assert r.status_code == 204 and "/login" in r.headers["hx-redirect"]


def test_ip_allowlist_denies(admin):
    get_settings().allowed_ips = "192.168.1.0/24"
    denied = TestClient(app, client=("10.0.0.5", 1)).get("/login")
    allowed = TestClient(app, client=("192.168.1.9", 1)).get("/login")
    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_duplicate_tag_and_serial(client, make_asset):
    make_asset("LT-1", "SN-1")
    r = client.post("/assets/new", data=asset_data("lt-1", "SN-2"))
    assert r.status_code == 422 and "Asset Tag ID already exists." in r.text
    r = client.post("/assets/new", data=asset_data("LT-9", "sn-1"))
    assert r.status_code == 422 and "Serial number already exists." in r.text


def test_warranty_before_purchase_rejected(client):
    today = date.today()
    r = client.post(
        "/assets/new",
        data=asset_data(purchase_date=today.isoformat(), warranty_expiry=(today - timedelta(days=1)).isoformat()),
    )
    assert r.status_code == 422 and "cannot be before the purchase date" in r.text


def test_checkout_checkin_flow(client, db, admin, make_asset, person_and_location):
    person, loc = person_and_location
    asset = make_asset()
    r = client.post(
        f"/checkout/{asset.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT", "notes": "n"},
    )
    assert r.status_code == 303
    db.expire_all()
    a = db.get(Asset, asset.id)
    assert a.status == "checked_out" and a.department == "IT"

    r = client.post(f"/checkin/{asset.id}", data={"notes": "back"})
    assert r.status_code == 303
    db.expire_all()
    a = db.get(Asset, asset.id)
    assert a.status == "available" and a.department is None and a.last_used_by == "Asha Rao"
    rows = db.scalars(select(AssetAssignment).where(AssetAssignment.asset_id == asset.id)).all()
    assert len(rows) == 1 and rows[0].checkin_at is not None

    r = client.get(f"/assets/{asset.id}")
    assert "Assignment history" in r.text and "Asha Rao" in r.text


def test_checkout_requires_fields(client, make_asset):
    asset = make_asset()
    r = client.post(f"/checkout/{asset.id}", data={"notes": "x"})
    assert r.status_code == 422 and r.text.count("This field is required.") >= 3


def test_double_checkout_blocked_concurrently(admin, make_asset, person_and_location):
    person, loc = person_and_location
    asset = make_asset()
    form, _ = validate_form(
        CheckoutForm, {"employee_id": person.id, "location_id": loc.id, "department": "IT"}
    )
    barrier = threading.Barrier(2)
    results = []

    def worker():
        s = SessionLocal()
        try:
            barrier.wait()
            assignments.checkout(s, s.get(type(admin), admin.id), asset.id, form)
            s.commit()
            results.append("ok")
        except FormError:
            s.rollback()
            results.append("blocked")
        finally:
            s.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sorted(results) == ["blocked", "ok"]
    s = SessionLocal()
    assert s.scalar(select(func.count()).select_from(AssetAssignment)) == 1
    s.close()


def test_retire_and_delete_blocked_while_checked_out(client, db, make_asset, person_and_location):
    person, loc = person_and_location
    asset = make_asset()
    client.post(
        f"/checkout/{asset.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT"},
    )
    for action in ("retire", "delete"):
        r = client.post(f"/assets/{asset.id}/{action}")
        assert r.status_code == 303
    db.expire_all()
    a = db.get(Asset, asset.id)
    assert a.status == "checked_out" and a.deleted_at is None

    client.post(f"/checkin/{asset.id}", data={"notes": ""})
    client.post(f"/assets/{asset.id}/retire")
    db.expire_all()
    assert db.get(Asset, asset.id).status == "retired"
    client.post(f"/assets/{asset.id}/delete")
    db.expire_all()
    assert db.get(Asset, asset.id).deleted_at is not None


def test_warranty_job_is_idempotent(db, admin, make_asset):
    today = date.today()
    make_asset("W1", "S-W1", warranty_expiry=(today + timedelta(days=20)).isoformat())
    make_asset("W2", "S-W2", warranty_expiry=(today + timedelta(days=5)).isoformat())
    make_asset("W3", "S-W3", warranty_expiry=(today - timedelta(days=8)).isoformat(),
               purchase_date=(today - timedelta(days=500)).isoformat())  # fmt: skip
    make_asset("W4", "S-W4")  # far in the future: no notification
    first = run_warranty_job(db, today)
    db.commit()
    assert first == 3  # one active user x three assets
    again = run_warranty_job(db, today)
    db.commit()
    assert again == 0
    total = db.scalar(
        select(func.count()).select_from(Notification).where(Notification.dedupe_key.like("warranty:%"))
    )
    assert total == 3


def test_cron_endpoint_requires_secret(client):
    c = TestClient(app, follow_redirects=False)
    assert c.get("/internal/cron/warranty").status_code == 401
    ok = c.get("/internal/cron/warranty", headers={"Authorization": "Bearer cron-test"})
    assert ok.status_code == 200


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (40, 40), "red").save(buf, "PNG")
    return buf.getvalue()


def test_photo_rejects_renamed_exe_and_accepts_png(client, db):
    bad = client.post(
        "/assets/new",
        data=asset_data(),
        files={"photo": ("evil.png", b"MZ\x90\x00 not an image", "image/png")},
    )
    assert bad.status_code == 422 and "not a valid image" in bad.text
    wrong_ext = client.post(
        "/assets/new", data=asset_data(), files={"photo": ("a.exe", _png_bytes(), "image/png")}
    )
    assert wrong_ext.status_code == 422 and "JPG, JPEG or PNG" in wrong_ext.text

    good = client.post(
        "/assets/new", data=asset_data(), files={"photo": ("ok.png", _png_bytes(), "image/png")}
    )
    assert good.status_code == 303
    name = db.scalar(select(Asset.photo_name))
    assert client.get(f"/media/{name}").headers["content-type"] == "image/png"
    anon = TestClient(app, follow_redirects=False)
    assert anon.get(f"/media/{name}").status_code == 303  # not public


def test_search_by_employee_name(client, make_asset, person_and_location):
    person, loc = person_and_location
    a1 = make_asset("LT-1", "SN-1")
    make_asset("LT-2", "SN-2")
    client.post(
        f"/checkout/{a1.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT"},
    )
    r = client.get("/assets?q=asha", headers={"HX-Request": "true"})
    assert "LT-1" in r.text and "LT-2" not in r.text
    none = client.get("/assets?q=zzzz", headers={"HX-Request": "true"})
    assert "No matching records found." in none.text


def test_empty_states(client):
    assert "No assets found." in client.get("/assets").text
    assert "No available assets found." in client.get("/checkout").text
    assert "No assigned assets found." in client.get("/checkin").text
    assert "No upcoming warranty expirations." in client.get("/warranty").text
    assert "No notifications available." in client.get("/notifications").text


def test_reveal_password_is_audited(client, db, make_asset):
    asset = make_asset(last_password="s3cret!")
    assert asset.last_password_enc and "s3cret" not in asset.last_password_enc
    assert "s3cret" not in client.get(f"/assets/{asset.id}").text
    r = client.post(f"/assets/{asset.id}/reveal-password")
    assert "s3cret!" in r.text
    audit = client.get("/audit?module=assets").text
    assert "Password Revealed" in audit


def test_user_limit_and_health(client, db):
    assert client.get("/healthz").json()["db"] == "up"
    for i in range(5):
        r = client.post(
            "/users/new", data={"name": f"U{i}", "email": f"u{i}@example.com", "password": "longenough1"}
        )
        assert r.status_code == 303
    r = client.post(
        "/users/new", data={"name": "X", "email": "x@example.com", "password": "longenough1"}
    )
    assert r.status_code == 422 and "maximum of 6" in r.text


def test_audit_logs_login_logout_profile(client):
    client.post("/profile/edit", data={"name": "New Name", "email": "admin@example.com"})
    client.post("/logout")
    c2 = TestClient(app, client=("10.0.0.5", 1), follow_redirects=False)
    c2.post("/login", data={"email": "admin@example.com", "password": PASSWORD})
    page = c2.get("/audit").text
    for label in ("Login", "Logout", "Profile Updated"):
        assert label in page


_ = pytest, CheckinForm
