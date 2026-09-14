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

## Environment variables

This repository uses a required `.env` file for local runs and for `gunicorn run:app`. Create it from the example:

```bash
cp .env.example .env
```

- `FLASK_ENV`
   - Set to `production` in production (used to default `SESSION_COOKIE_SECURE=1`).

- `SECRET_KEY`
   - Flask session signing key. Set this to a long random value in production.

- `FLASK_DEBUG`
   - `1`/`true` enables debug mode when running `python run.py`.
   - Default is off.

- `HOST`, `PORT`
   - Bind address/port when running `python run.py`.
   - Defaults: `HOST=127.0.0.1`, `PORT=5000`.

- `SESSION_COOKIE_SECURE`
   - `1` forces the session cookie to be HTTPS-only.
   - Defaults to `1` when `FLASK_ENV=production`, otherwise `0`.

- `SESSION_COOKIE_SAMESITE`
   - Defaults to `Lax`.

- `ENABLE_HSTS`
   - Optional: set to `1` to emit `Strict-Transport-Security` from Flask.
   - Many setups prefer enabling HSTS in nginx instead.

Example (production-ish):

```bash
export FLASK_ENV=production
export SECRET_KEY='change-me-to-a-long-random-string'
export SESSION_COOKIE_SECURE=1
export SESSION_COOKIE_SAMESITE=Lax
```

5. **Access the application**
   - Open your browser and go to `/`
   - Admin Dashboard: `/admin`
   - User Dashboard: `/user`
   - Device Status: `/status`
   - Activity Log: `/log`

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
RK_depot/
├── .env.example              # Example runtime configuration
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # SQLAlchemy models
│   ├── routes.py             # Route handlers
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── page.html          # Flatpage template
│   │   ├── about.html         # About page
│   │   ├── privacy.html       # Privacy page
│   │   ├── admin/             # Admin templates
│   │   ├── user/              # User templates
│   │   ├── status/            # Status page template
│   │   └── log/               # Log templates
│   └── static/
│       ├── css/
│       │   └── style.css     # Custom styles
│       └── robots.txt
├── pages/                    # Markdown content served as flatpages
│   ├── lagsutstyr.md         # Suggested team equipment
│   ├── personlig-utstyr.md   # Suggested personal equipment
│   └── staende-ordre.md      # Standing orders
├── scripts/
│   ├── release_all_booked.py # Release all currently booked devices
│   ├── seed_devices.py       # Seed the database with devices
│   ├── test_booking.py       # Booking flow test
│   └── test_post_booking.py  # POST booking flow test
├── device_booking.db_bak     # Database backup
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Flatpages

Informational content is managed as Markdown files in the top-level `pages/` directory using Flask-FlatPages. Files must use the `.md` extension. The application configures this directory as the FlatPages root and renders each page with `app/templates/page.html`. Pages are served at `/info/<path>/`.

### Creating a flatpage

1. Create a Markdown file in `pages/`, for example `pages/utstyrskontroll.md`.
2. Add YAML frontmatter with a `title`:

   ```markdown
   ---
   title: Utstyrskontroll
   ---

   # Utstyrskontroll

   Content written in Markdown.
   ```

3. Visit the corresponding URL under `/info/`: `pages/utstyrskontroll.md` is available at `/info/utstyrskontroll/`.

Flatpages can link to one another with the same URL pattern, for example `/info/personlig-utstyr/`. The page content is converted to HTML by Flask-FlatPages and inserted into `page.html`; only trusted repository content should be published because the template renders the generated HTML directly.

### Database errors
To reset the database, delete `device_booking.db` and run the application again to create a fresh database.

## Support

For issues or questions, please check the template files and routes to understand the application flow.

## License

This project is provided as-is for internal use.
