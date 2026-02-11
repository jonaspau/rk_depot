#!/usr/bin/env python3
import os, sys
# Ensure project root is on sys.path when running this script from scripts/ folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Device

app = create_app()

with app.app_context():
    created = 0
    skipped = 0
    for i in range(1, 31):
        device_id = f"{i:03}"
        # Alternate names
        name = 'Nødnett' if i % 2 == 1 else 'Nettbrett'
        category = name
        # First 15 -> Ski, next 15 -> Oppegård
        location = 'Ski' if i <= 15 else 'Oppegård'
        status = 'available'

        if db.session.get(Device, device_id) is not None:
            skipped += 1
            continue

        d = Device(id=device_id, name=name, category=category, location=location, status=status)
        db.session.add(d)
        created += 1

    db.session.commit()
    print(f"Created {created} devices, skipped {skipped} already-present ids.")
