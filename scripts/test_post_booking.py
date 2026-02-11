from app import create_app, db
from app.models import Device, Booking
from datetime import datetime

app = create_app()
with app.app_context():
    # pick 4 available devices
    devices = Device.query.filter(Device.status=='available').order_by(Device.name, Device.id).limit(4).all()
    ids = [d.id for d in devices]
    print('Selected ids:', ids)

    before = Booking.query.count()
    client = app.test_client()
    # send POST as form data with multiple device_ids
    data = {'user_name':'test_client','device_ids': ids}
    resp = client.post('/user/book', data=data, follow_redirects=True)
    print('POST status code:', resp.status_code)
    after = Booking.query.count()
    print('Bookings before:', before, 'after:', after, 'added:', after-before)
    for b in Booking.query.filter_by(user_name='test_client').all():
        print('booking', b.id, b.device_id)
