"""Admin CLI: python -m app.cli <create-admin|seed-demo|run-warranty-job>."""

from __future__ import annotations

import argparse
import getpass
import sys
from datetime import date, timedelta

from app.core.logging import configure_logging
from app.db import SessionLocal, init_db
from app.schemas.common import validate_form
from app.schemas.forms import AssetForm, LocationForm, PersonForm, UserCreateForm
from app.services import assets, locations, people, users
from app.services.common import FormError
from app.services.warranty import run_warranty_job


def init_database(_args) -> int:
    init_db()
    print("Database tables are ready.")
    return 0


def create_admin(args) -> int:
    init_db()
    password = args.password or getpass.getpass("Password (min 8 chars): ")
    form, errors = validate_form(
        UserCreateForm, {"name": args.name, "email": args.email, "password": password}
    )
    if form is None:
        print("Invalid input:", errors)
        return 1
    with SessionLocal() as db:
        try:
            user = users.create_user(db, None, form)
            db.commit()
        except FormError as exc:
            print("Error:", exc)
            return 1
    print(f"Created admin {user.email} (id={user.id})")
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
    p = sub.add_parser("create-admin", help="Create an administrator account")
    p.add_argument("--name", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--password", help="Omit to be prompted")
    p.set_defaults(func=create_admin)
    sub.add_parser("init-db", help="Create database tables").set_defaults(func=init_database)
    sub.add_parser("seed-demo", help="Insert sample data").set_defaults(func=seed_demo)
    sub.add_parser("run-warranty-job", help="Create warranty notifications now").set_defaults(
        func=warranty_job
    )
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
