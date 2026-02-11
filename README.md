# RK depot

A web-based application for managing device bookings and tracking their usage. Built with Flask and SQLite.
The current setup is using gunicorn in a gcloud vm. Any adaptations may be required for other usage.

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/RK_depot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Admin Dashboard: `http://localhost:5000/admin`
   - User Dashboard: `http://localhost:5000/user`
   - Device Status: `http://localhost:5000/status`
   - Activity Log: `http://localhost:5000/log`

## Database

The application uses SQLite for data storage. The database file (`device_booking.db`) is automatically created when you first run the application.

### Database Schema

#### Devices Table
- `id` (STRING, Primary Key): Unique device identifier
- `name` (STRING): Device name
- `category` (STRING): Device category/type
- `location` (STRING): Device location
- `status` (STRING): Current status (available/booked)
- `current_user` (STRING): User currently holding the device
- `booked_at` (DATETIME): When the device was booked

#### Bookings Table
- `id` (INTEGER, Primary Key): Booking ID
- `device_id` (STRING, Foreign Key): Reference to device
- `user_name` (STRING): Name of the person booking the device
- `booked_at` (DATETIME): When the device was booked
- `handed_in_at` (DATETIME): When the device was handed in
- `hand_in_comment` (TEXT): Comments provided at hand-in
- `status` (STRING): Booking status (active/completed)

#### Activity Log Table
- `id` (INTEGER, Primary Key): Log entry ID
- `device_id` (STRING, Foreign Key): Reference to device
- `user_name` (STRING): User performing the action
- `action` (STRING): Action type (booked/handed_in)
- `timestamp` (DATETIME): When the action occurred
- `comment` (TEXT): Associated comments

## Usage

### Admin Functions

1. **Add Device**
   - Navigate to Admin Dashboard → Add New Device
   - Enter device ID (unique), name, category, and location
   - Click "Add Device"

2. **Edit Device**
   - Click "Edit" next to a device in the admin dashboard
   - Update the device information
   - Click "Save Changes"

3. **Delete Device**
   - Click "Delete" next to a device
   - Confirm deletion in the popup dialog

4. **View Device Log**
   - Click "Log" next to a device to see its activity history

### User Functions

1. **Book Devices**
   - Go to User Dashboard → Book Devices
   - Enter your name
   - Select one or more available devices
   - Click "Book Selected Devices"
   - Devices will be marked as unavailable for others

2. **Hand In Device**
   - Go to User Dashboard → Hand In Device
   - Enter your name
   - Select the device from the dropdown
   - Optionally add comments about damage or issues
   - Click "Hand In Device"
   - Device becomes available again

### View Information

1. **Device Status Page**
   - See all devices with their current status
   - View who currently has each booked device
   - Check when each device was booked

2. **Activity Log**
   - View all bookings and hand-ins with timestamps
   - Filter by device
   - See comments provided at hand-in
   - Pagination for easier browsing

## Accessibility

This application is built with accessibility in mind:
- Semantic HTML structure
- Proper label associations with form inputs
- Skip-to-main-content link
- Keyboard navigation support
- High contrast status indicators
- Descriptive button labels

## Technical Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML5 with Pico CSS framework
- **Styling**: Custom CSS with accessibility enhancements

## Project Structure

```
RK devcelibrary/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # SQLAlchemy models
│   ├── routes.py             # Route handlers
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── admin/            # Admin templates
│   │   ├── user/             # User templates
│   │   ├── status/           # Status page template
│   │   └── log/              # Log templates
│   └── static/
│       └── css/
│           └── style.css     # Custom styles
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Database errors
To reset the database, delete `device_booking.db` and run the application again to create a fresh database.

## Support

For issues or questions, please check the template files and routes to understand the application flow.

## License

This project is provided as-is for internal use.
