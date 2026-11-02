import os

from cryptography.fernet import Fernet

TEST_DB = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://assetify:assetify@localhost:5434/assetify_test"
)
os.environ["DATABASE_URL"] = TEST_DB
os.environ["SECRET_KEY"] = "test-secret"
os.environ["FIELD_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["ENV"] = "dev"
os.environ["ALLOWED_IPS"] = ""
os.environ["CLIENT_IP_HEADER"] = ""
os.environ["CRON_SECRET"] = "cron-test"

from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import SessionLocal, get_engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.common import validate_form  # noqa: E402
from app.schemas.forms import AssetForm, LocationForm, PersonForm, UserCreateForm  # noqa: E402
from app.services import assets, locations, people, users  # noqa: E402

PASSWORD = "Test#Pass123"


@pytest.fixture(scope="session", autouse=True)
def _schema():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("drop schema public cascade"))
        conn.execute(text("create schema public"))
    init_db()
    yield


@pytest.fixture(autouse=True)
def _clean():
    yield
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "truncate audit_logs, notifications, asset_assignments, assets, employees, "
                "locations, users restart identity cascade"
            )
        )
    get_settings().allowed_ips = ""


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def admin(db):
    form, _ = validate_form(
        UserCreateForm, {"name": "Admin", "email": "admin@example.com", "password": PASSWORD}
    )
    user = users.create_user(db, None, form)
    db.commit()
    return user


@pytest.fixture
def client(admin):
    c = TestClient(app, client=("10.0.0.5", 5000), follow_redirects=False)
    resp = c.post("/login", data={"email": "admin@example.com", "password": PASSWORD})
    assert resp.status_code == 303, resp.text
    return c


def asset_data(tag="LT-1", serial="SN-1", **over):
    today = date.today()
    data = dict(
        asset_tag_id=tag, description="Test laptop", brand="Dell", model="X1", serial_number=serial,
        purchase_date=(today - timedelta(days=100)).isoformat(),
        warranty_expiry=(today + timedelta(days=400)).isoformat(),
    )  # fmt: skip
    data.update(over)
    return data


@pytest.fixture
def make_asset(db, admin):
    def _make(tag="LT-1", serial="SN-1", **over):
        form, errors = validate_form(AssetForm, asset_data(tag, serial, **over))
        assert form, errors
        asset = assets.create_asset(db, admin, form)
        db.commit()
        return asset

    return _make


@pytest.fixture
def person_and_location(db, admin):
    lform, _ = validate_form(
        LocationForm,
        dict(name="HQ", floor="1", building_name="Tower", area="Baner", pincode="411045",
             district="Pune", state="MH"),
    )  # fmt: skip
    loc = locations.create_location(db, admin, lform)
    pform, errors = validate_form(
        PersonForm,
        dict(name="Asha Rao", employee_code="E1", mobile="9876543210", email="asha@example.com",
             address="Somewhere", pincode="411001", location_id=loc.id),
    )  # fmt: skip
    assert pform, errors
    person = people.create_person(db, admin, pform)
    db.commit()
    return person, loc

