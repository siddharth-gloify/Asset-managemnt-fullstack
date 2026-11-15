"""Coverage for the November 2026 feedback batch: one test per requested change."""

from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import Asset, AssetAssignment, AssetType
from tests.conftest import asset_data

_ = pytest


# 1. Extensible asset types: add a new one inline, then use it on a device.
def test_can_add_new_asset_type_and_use_it(client, db):
    r = client.post("/asset-types/inline", data={"label": "Security Camera"})
    assert r.status_code == 200
    assert db.scalar(select(AssetType.id).where(AssetType.key == "security_camera")) is not None

    r = client.post("/assets/new", data=asset_data(asset_type="security_camera"))
    assert r.status_code == 303
    asset = db.scalar(select(Asset).where(Asset.asset_tag_id == "LT-1"))
    assert asset.asset_type == "security_camera"

    bad = client.post("/assets/new", data=asset_data("LT-2", "SN-2", asset_type="not_a_real_type"))
    assert bad.status_code == 422 and "Select a valid asset type." in bad.text


# 2. Purchase date / warranty are optional now (some devices have no paperwork).
def test_purchase_and_warranty_dates_are_optional(client, db):
    data = asset_data()
    data["purchase_date"] = ""
    data["warranty_expiry"] = ""
    r = client.post("/assets/new", data=data)
    assert r.status_code == 303
    asset = db.scalar(select(Asset).where(Asset.asset_tag_id == "LT-1"))
    assert asset.purchase_date is None and asset.warranty_expiry is None


# 3. Mobile numbers must be exactly 10 digits.
def test_mobile_number_must_be_exactly_10_digits(client):
    base = dict(name="X", employee_code="E-9", email="x9@example.com", address="addr",
                pincode="411045", location_id="")  # fmt: skip
    short = client.post("/people/new", data={**base, "mobile": "98765432"})
    assert short.status_code == 422 and "10 digits" in short.text
    long_ = client.post("/people/new", data={**base, "mobile": "987654321099"})
    assert long_.status_code == 422 and "10 digits" in long_.text


# 4. Location pincode must be exactly 6 digits.
def test_location_pincode_must_be_exactly_6_digits(client):
    base = dict(name="Branch Office", floor="1", building_name="Tower", area="Baner", district="Pune", state="MH")
    short = client.post("/locations/new", data={**base, "pincode": "4110"})
    assert short.status_code == 422 and "6 digits" in short.text
    ok = client.post("/locations/new", data={**base, "pincode": "411045"})
    assert ok.status_code == 303


# 5. The add-device "Last Password" field has a show/hide toggle.
def test_last_password_field_has_toggle(client):
    r = client.get("/assets/new")
    assert 'data-hs-toggle-password' in r.text and 'target": "#f-last_password"' in r.text


# 6. Check-out lets you backdate the check-out date (for assignments made before the app existed).
def test_checkout_can_be_backdated(client, db, make_asset, person_and_location):
    person, loc = person_and_location
    asset = make_asset()
    backdate = (date.today() - timedelta(days=30)).isoformat()
    r = client.post(
        f"/checkout/{asset.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT",
              "checkout_date": backdate},
    )  # fmt: skip
    assert r.status_code == 303
    assignment = db.scalar(select(AssetAssignment).where(AssetAssignment.asset_id == asset.id))
    local_date = assignment.checkout_at.astimezone(get_settings().tz).date()
    assert local_date.isoformat() == backdate

    future = (date.today() + timedelta(days=1)).isoformat()
    asset2 = make_asset("LT-2", "SN-2")
    bad = client.post(
        f"/checkout/{asset2.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT",
              "checkout_date": future},
    )  # fmt: skip
    assert bad.status_code == 422 and "cannot be in the future" in bad.text


# 7. Retired assets are visible (filter + stat tile), and available/maintenance laptops can change status.
def test_retired_assets_are_visible_and_status_can_change(client, db, make_asset):
    asset = make_asset()
    assert client.post(f"/assets/{asset.id}/maintenance").status_code == 303
    db.expire_all()
    assert db.get(Asset, asset.id).status == "under_maintenance"
    assert client.post(f"/assets/{asset.id}/maintenance").status_code == 303
    db.expire_all()
    assert db.get(Asset, asset.id).status == "available"

    assert client.post(f"/assets/{asset.id}/retire").status_code == 303
    db.expire_all()
    assert db.get(Asset, asset.id).status == "retired"

    listing = client.get("/assets?status=retired").text
    assert asset.asset_tag_id in listing and 'value="retired" selected' in listing
    view = client.get(f"/assets/{asset.id}").text
    assert "Retired" in view


# 8. CSV export of the assets list.
def test_assets_export_csv(client, make_asset):
    make_asset()
    r = client.get("/assets/export")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=assets.csv" in r.headers["content-disposition"]
    assert "LT-1" in r.text and "Asset Tag Id" in r.text


# 9. Department can be set directly on the asset form (not only via check-out).
def test_department_field_on_asset_add_and_edit(client, db):
    r = client.post("/assets/new", data=asset_data(department="Finance"))
    assert r.status_code == 303
    asset = db.scalar(select(Asset).where(Asset.asset_tag_id == "LT-1"))
    assert asset.department == "Finance"

    r = client.post("/assets/new", data=asset_data("LT-2", "SN-2"))
    asset2 = db.scalar(select(Asset).where(Asset.asset_tag_id == "LT-2"))
    edit_data = asset_data("LT-2", "SN-2", department="Legal")
    r = client.post(f"/assets/{asset2.id}/edit", data=edit_data)
    assert r.status_code == 303
    db.expire_all()
    assert db.get(Asset, asset2.id).department == "Legal"


# 10. Assigned-to name shows up on the assets list and the check-in list once a device is checked out.
def test_assigned_to_name_shown_on_lists(client, make_asset, person_and_location):
    person, loc = person_and_location
    asset = make_asset()
    client.post(
        f"/checkout/{asset.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "IT"},
    )
    assets_list = client.get("/assets").text
    assert person.name in assets_list
    checkin_list = client.get("/checkin").text
    assert person.name in checkin_list


# 11. Department/OS/Memory/Hard Disk columns appear on the check-in and check-out tables.
def test_device_detail_columns_on_checkin_and_checkout_lists(client, make_asset, person_and_location):
    person, loc = person_and_location
    make_asset("LT-1", "SN-1", os="Windows 11", memory="16 GB", hard_disk="512 GB SSD")
    checkout_list = client.get("/checkout").text
    assert "Windows 11" in checkout_list and "16 GB" in checkout_list and "512 GB SSD" in checkout_list

    asset = make_asset("LT-2", "SN-2", os="macOS", memory="8 GB", hard_disk="256 GB SSD")
    client.post(
        f"/checkout/{asset.id}",
        data={"employee_id": person.id, "location_id": loc.id, "department": "Design"},
    )
    checkin_list = client.get("/checkin").text
    assert "macOS" in checkin_list and "Design" in checkin_list and "8 GB" in checkin_list


# 12. People and locations now have a "View" detail popup, not just Edit.
def test_people_and_locations_have_view_detail(client, person_and_location):
    person, loc = person_and_location
    person_view = client.get(f"/people/{person.id}").text
    assert person.address in person_view and person.employee_code in person_view

    location_view = client.get(f"/locations/{loc.id}").text
    assert loc.building_name in location_view and loc.pincode in location_view
