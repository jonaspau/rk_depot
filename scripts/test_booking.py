from app import create_app, db
from app.models import Device, Booking, ActivityLog
from datetime import datetime

app = create_app()
with app.app_context():
    # choose four available devices
    devices = Device.query.filter(Device.status=='available').order_by(Device.name, Device.id).limit(4).all()
    ids = [d.id for d in devices]
    print('Selected ids:', ids)
    user_name = 'test_user_auto'
    before = Booking.query.count()
    # mimic booking route loop
    for device_id in ids:
        device = Device.query.get(device_id)
        if device and device.status == 'available':
            booking = Booking(device_id=device_id, user_name=user_name, booked_at=datetime.utcnow())
            device.status = 'booked'
            device.current_user = user_name
            device.booked_at = datetime.utcnow()
            log = ActivityLog(device_id=device_id, user_name=user_name, action='booked', timestamp=datetime.utcnow())
            db.session.add(booking)
            db.session.add(log)
    db.session.commit()
    after = Booking.query.count()
    print('Bookings before:', before, 'after:', after, 'added:', after-before)
    # show bookings for test_user
    b = Booking.query.filter_by(user_name=user_name).all()
    for booking in b:
        print('booking', booking.id, booking.device_id, booking.status)
