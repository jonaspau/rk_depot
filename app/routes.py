from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from app import db
from app.models import Device, Booking, ActivityLog
from sqlalchemy import or_, and_

# Create blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')
status_bp = Blueprint('status', __name__, url_prefix='/status')
log_bp = Blueprint('log', __name__, url_prefix='/log')
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return redirect(url_for('user.user_dashboard'))

# Admin Routes
@admin_bp.route('/')
def admin_dashboard():
    devices = Device.query.order_by(Device.name, Device.id).all()
    return render_template('admin/dashboard.html', devices=devices, show_menu=True)


@admin_bp.route('/add-device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        device_id = request.form.get('device_id')
        name = request.form.get('name')
        category = request.form.get('category')
        location = request.form.get('location')

        # Check if device ID already exists
        if Device.query.filter_by(id=device_id).first():
            flash('IDen er allerede registrert', 'error')
            return redirect(url_for('admin.add_device'))

        device = Device(
            id=device_id,
            name=name,
            category=category,
            location=location
        )

        db.session.add(device)
        db.session.commit()

        flash(f'{device_id} - {name} lagt til', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_device.html')


@admin_bp.route('/edit-device/<device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)

    if request.method == 'POST':
        device.name = request.form.get('name')
        device.category = request.form.get('category')
        device.location = request.form.get('location')

        # Admin can set/clear current user and status
        current_user = request.form.get('current_user')
        status = request.form.get('status')
        if current_user:
            device.current_user = current_user
            device.booked_at = datetime.utcnow()
            device.status = 'booked'
            # create a booking record if none active exists for this device/user
            existing = Booking.query.filter_by(device_id=device.id, user_name=current_user, status='active').first()
            if not existing:
                booking = Booking(device_id=device.id, user_name=current_user, booked_at=datetime.utcnow())
                db.session.add(booking)
                log = ActivityLog(device_id=device.id, user_name=current_user, action='booked', timestamp=datetime.utcnow())
                db.session.add(log)
        else:
            # if admin cleared user and selected available, remove booking state
            if status == 'available' or not status:
                device.current_user = None
                device.booked_at = None

        if status:
            device.status = status

        db.session.commit()
        flash(f'{device.name} {device.id} endret', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_device.html', device=device)


@admin_bp.route('/delete-device/<device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    device_name = device.name

    db.session.delete(device)
    db.session.commit()

    flash(f'{device_name} {device_id} fjernet', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/update-status/<device_id>', methods=['POST'])
def update_device_status(device_id):
    device = Device.query.get_or_404(device_id)
    new_status = request.form.get('status')

    # Validate status
    if new_status not in ['available', 'booked', 'unavailable']:
        flash('Ugyldig status', 'error')
        return redirect(url_for('admin.admin_dashboard'))

    device.status = new_status

    # If marking as unavailable or available, clear the current user and booking info
    if new_status in ['unavailable', 'available']:
        device.current_user = None
        device.booked_at = None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Feil ved oppdatering av status: {e}', 'error')
        return redirect(url_for('admin.admin_dashboard'))

    flash(f'{device.name} {device.id} status endret til {new_status}', 'success')
    return redirect(url_for('admin.admin_dashboard'))


# User Routes
@user_bp.route('/')
def user_dashboard():
    session_user = session.get('user_name')
    category_filter = request.args.get('category')

    # Get all available and booked devices (exclude unavailable)
    available_devices = Device.query.filter(Device.status.in_(['available', 'booked'])).order_by(Device.name, Device.id).all()

    # Get distinct categories for filter
    all_categories = db.session.query(Device.category).distinct().order_by(Device.category).all()
    categories = [cat[0] for cat in all_categories if cat[0]]

    # Filter by category if provided
    if category_filter:
        available_devices = [d for d in available_devices if d.category == category_filter]

    # Get user's booked devices
    if session_user:
        user_booked = Device.query.filter_by(current_user=session_user).order_by(Device.name, Device.id).all()
    else:
        user_booked = []

    return render_template('user/dashboard.html', devices=available_devices, user_booked=user_booked,
                         session_user=session_user, categories=categories, selected_category=category_filter, show_menu=False)


@user_bp.route('/set-user', methods=['POST'])
def set_user():
    new_user = request.form.get('user_name')
    next_page = request.form.get('next') or url_for('user.user_dashboard')
    if new_user:
        session['user_name'] = new_user
        session.permanent = True
        flash(f'Logget inn som {new_user}', 'success')
    else:
        session.pop('user_name', None)
        flash('Logget ut', 'success')
    return redirect(next_page)


@user_bp.route('/change-user', methods=['GET'])
def change_user():
    # Render a small standalone change-user form. It posts to /user/set-user
    next_page = request.args.get('next') or request.referrer or url_for('user.user_dashboard')
    session_user = session.get('user_name')
    return render_template('user/change_user.html', session_user=session_user, next=next_page, show_menu=False)


@user_bp.route('/book', methods=['GET', 'POST'])
def book_device():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        # accept both `device_ids` and `device_ids[]` to be robust across browsers/UI
        device_ids = request.form.getlist('device_ids') + request.form.getlist('device_ids[]')
        # filter out any empty values
        device_ids = [d for d in device_ids if d]

        if not device_ids:
            flash('Velg minst en enhet', 'error')
            return redirect(url_for('user.book_device'))

        for device_id in device_ids:
            device = Device.query.get(device_id)
            # Allow booking when device is explicitly available, or when it's marked booked
            # but not assigned to any user (current_user is None or empty string).
            can_book = False
            if device:
                if device.status == 'available':
                    can_book = True
                elif device.status == 'booked' and (device.current_user is None or device.current_user == ''):
                    can_book = True

            if device and can_book:
                # Create booking
                booking = Booking(
                    device_id=device_id,
                    user_name=user_name,
                    booked_at=datetime.utcnow()
                )

                # Update device status
                device.status = 'booked'
                device.current_user = user_name
                device.booked_at = datetime.utcnow()

                # Log activity
                log = ActivityLog(
                    device_id=device_id,
                    user_name=user_name,
                    action='booked',
                    timestamp=datetime.utcnow()
                )

                db.session.add(booking)
                db.session.add(log)

        # Remember the user in session for convenience during hand-in
        session['user_name'] = user_name
        session.permanent = True

        db.session.commit()
        flash(f'Tok ut {len(device_ids)} enhet(er)', 'success')
        return redirect(url_for('user.user_dashboard'))

    # GET: support filtering by category and location
    category_filter = request.args.get('category')
    location_filter = request.args.get('location')

    # Devices that can be booked: either explicitly 'available' or marked 'booked' but not assigned to any user
    # Only show explicitly available devices for booking
    devices = Device.query.filter_by(status='available').order_by(Device.name, Device.id).all()

    # Distinct categories and locations for filters
    all_categories = db.session.query(Device.category).distinct().order_by(Device.category).all()
    categories = [c[0] for c in all_categories if c[0]]
    all_locations = db.session.query(Device.location).distinct().order_by(Device.location).all()
    locations = [l[0] for l in all_locations if l[0]]

    if category_filter:
        devices = [d for d in devices if d.category == category_filter]
    if location_filter:
        devices = [d for d in devices if d.location == location_filter]

    session_user = session.get('user_name')
    return render_template('user/book_device.html', devices=devices, session_user=session_user, show_menu=False,
                           categories=categories, locations=locations,
                           selected_category=category_filter, selected_location=location_filter)


@user_bp.route('/hand-in', methods=['GET', 'POST'])
def hand_in_device():
    if request.method == 'POST':
        # Support handing in multiple devices at once
        form_user = request.form.get('user_name')
        session_user = session.get('user_name')
        user_name = form_user or session_user
        intent = request.form.get('intent')
        device_ids = request.form.getlist('device_ids') + request.form.getlist('device_ids[]')
        device_ids = [d for d in device_ids if d]
        comment = request.form.get('comment')

        # If no session user is set, allow a first submit to set the user and refresh.
        if (intent == 'set_user' or (not device_ids and form_user and not session_user)):
            session['user_name'] = form_user
            session.permanent = True
            return redirect(url_for('user.hand_in_device'))

        if not user_name:
            flash('Skriv inn brukernavn', 'error')
            return redirect(url_for('user.hand_in_device'))

        if not device_ids:
            flash('Velg minst en enhet for å levere', 'error')
            return redirect(url_for('user.hand_in_device'))

        handed_in_count = 0
        for device_id in device_ids:
            device = Device.query.get(device_id)
            if not device:
                continue

            # Find the active booking for this user and device
            booking = Booking.query.filter_by(
                device_id=device_id,
                user_name=user_name,
                status='active'
            ).first()

            if booking:
                booking.handed_in_at = datetime.utcnow()
                booking.hand_in_comment = comment
                booking.status = 'completed'
                handed_in_count += 1

            # Update device status regardless (defensive)
            device.status = 'available'
            device.current_user = None
            device.booked_at = None

            # Log activity per device
            log = ActivityLog(
                device_id=device_id,
                user_name=user_name,
                action='handed_in',
                timestamp=datetime.utcnow(),
                comment=comment
            )
            db.session.add(log)

        db.session.commit()

        flash(f'Leverte {handed_in_count} enhet(er)', 'success')
        return redirect(url_for('user.user_dashboard'))

    # GET: show only active booked devices for the current user (if known)
    session_user = session.get('user_name')
    if session_user:
        booked_devices = db.session.query(Device, Booking).join(Booking).filter(
            Device.status == 'booked',
            Booking.status == 'active',
            Booking.user_name == session_user
        ).order_by(Device.name, Device.id).all()
        # extract devices only for display in booking-like layout
        devices = [device for device, booking in booked_devices]
    else:
        devices = []

    return render_template('user/hand_in_device.html', devices=devices, session_user=session_user, show_menu=False)


# Status Page
@status_bp.route('/')
def status_page():
    devices = Device.query.order_by(Device.name, Device.id).all()
    return render_template('status/status.html', devices=devices)


# Activity Log
@log_bp.route('/')
def activity_log():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=50)
    return render_template('log/activity_log.html', logs=logs)


@log_bp.route('/device/<device_id>')
def device_log(device_id):
    device = Device.query.get_or_404(device_id)
    logs = ActivityLog.query.filter_by(device_id=device_id).order_by(ActivityLog.timestamp.desc()).all()
    return render_template('log/device_log.html', device=device, logs=logs)
