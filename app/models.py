from app import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='available', nullable=False)  # available, booked
    current_user = db.Column(db.String(200))  # user currently holding the device
    booked_at = db.Column(db.DateTime)
    
    bookings = db.relationship('Booking', backref='device', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('ActivityLog', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.id}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'), nullable=False)
    user_name = db.Column(db.String(200), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    handed_in_at = db.Column(db.DateTime)
    hand_in_comment = db.Column(db.Text)
    status = db.Column(db.String(50), default='active', nullable=False)  # active, completed
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'), nullable=False)
    user_name = db.Column(db.String(200))
    action = db.Column(db.String(50), nullable=False)  # booked, handed_in
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    comment = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ActivityLog {self.id}>'
