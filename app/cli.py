"""Admin CLI: python -m app.cli <seed-demo|run-warranty-job>."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from app.config import get_settings
from app.core.logging import configure_logging
from app.db import SessionLocal, init_db
from app.schemas.common import validate_form
from app.schemas.forms import AssetForm, LocationForm, PersonForm
from app.services import assets, locations, people, users
from app.services.common import FormError
from app.services.warranty import run_warranty_job


def init_database(_args) -> int:
    init_db()
    print("Database tables are ready.")
    return 0


def seed_users(_args) -> int:
    rows = get_settings().seed_user_list
    if not rows:
        print("SEED_USERS is empty. Set it in .env as Name|email|password,Name|email|password")
        return 1
    init_db()
    with SessionLocal() as db:
        for line in users.sync_seed_users(db, rows):
            print(line)
        db.commit()
    return 0


def seed_demo(_args) -> int:
    today = date.today()
    with SessionLocal() as db:
        actor = None
        loc_form, _ = validate_form(
            LocationForm,
            dict(name="Head Office - Floor 2", floor="2", building_name="GLOIFY Tower", area="Baner",
                 pincode="411045", district="Pune", state="Maharashtra"),
        )  # fmt: skip
        try:
            loc = locations.create_location(db, actor, loc_form)
        except FormError:
            print("Demo data already present.")
            return 0
        person, _ = validate_form(
            PersonForm,
            dict(name="Asha Rao", employee_code="E-1001", mobile="9876543210", email="asha@example.com",
                 address="12 MG Road, Pune", pincode="411001", location_id=loc.id),
        )  # fmt: skip
        people.create_person(db, actor, person)
        samples = [
            ("LT-0001", "Dell Latitude 5440", "Dell", "Latitude 5440", "DL5440-001", 400, 60),
            ("LT-0002", "MacBook Air M2", "Apple", "MacBook Air M2", "MBA-M2-002", 700, 20),
            ("LT-0003", "Lenovo ThinkPad T14", "Lenovo", "ThinkPad T14", "TP-T14-003", 900, 200),
        ]
        for tag, desc, brand, model, serial, bought_days_ago, warranty_in_days in samples:
            form, errors = validate_form(
                AssetForm,
                dict(asset_tag_id=tag, description=desc, brand=brand, model=model, serial_number=serial,
                     purchase_date=(today - timedelta(days=bought_days_ago)).isoformat(),
                     warranty_expiry=(today + timedelta(days=warranty_in_days)).isoformat(),
                     os="Windows 11", memory="16 GB", hard_disk="512 GB SSD"),
            )  # fmt: skip
            assets.create_asset(db, actor, form)
        db.commit()
    print("Seeded demo location, person and 3 laptops.")
    return 0


def warranty_job(_args) -> int:
    with SessionLocal() as db:
        created = run_warranty_job(db)
        db.commit()
    print(f"Warranty job complete: {created} notification(s) created.")
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed-users", help="Create/update logins from SEED_USERS in .env").set_defaults(
        func=seed_users
    )
    sub.add_parser("init-db", help="Create database tables").set_defaults(func=init_database)
    sub.add_parser("seed-demo", help="Insert sample data").set_defaults(func=seed_demo)
    sub.add_parser("run-warranty-job", help="Create warranty notifications now").set_defaults(
        func=warranty_job
    )
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
