from app import create_app, db
from app.models import Device, Booking, ActivityLog
from datetime import datetime

app = create_app()
with app.app_context():
    # Release all active bookings and mark devices available
    active_bookings = Booking.query.filter_by(status='active').all()
    print(f"Found {len(active_bookings)} active bookings to complete.")
    released = 0
    for booking in active_bookings:
        device = Device.query.get(booking.device_id)
        booking.handed_in_at = datetime.utcnow()
        booking.status = 'completed'
        # update device
        if device:
            device.status = 'available'
            device.current_user = None
            device.booked_at = None
            released += 1
        # log the hand-in
        log = ActivityLog(device_id=booking.device_id, user_name=booking.user_name or 'system', action='handed_in', timestamp=datetime.utcnow(), comment='Released by admin script')
        db.session.add(log)

    db.session.commit()
    print(f"Released {released} devices and completed {len(active_bookings)} bookings.")
