# Shruti

Offline, audio-first assistive learning system for blind students.

## Features (Phase 1)

- Flask web application with accessible HTML layout
- SQLite database with full schema (9 tables with UUID primary keys)
- Accessible base layout with skip link and ARIA live regions
- Class picker screen with large, keyboard-accessible buttons
- High-contrast colors and large fonts (24px+)
- Full keyboard navigation support
- NVDA screen reader compatible

## Tech Stack

- Python 3.11+
- Flask 3.0
- SQLite
- pyttsx3 (for future audio generation)
- pdfplumber (for future PDF processing)
- Vanilla HTML/CSS/JS

## Prerequisites

- Windows 10/11
- Python 3.11 or higher
- NVDA screen reader (for blind students)
- Hindi SAPI5 voice (optional, for future Hindi audio support)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Shruti
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

6. Verify SAPI5 voices (optional, for future phases):
   ```bash
   python scripts/verify_voices.py
   ```

## Quick Start

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and go to: http://127.0.0.1:5000

3. You will see the class picker screen with three class buttons (Class 10, Class 11, Class 12)

## Project Status

- Phase 1: ✅ Complete (Skeleton + Database + Base Accessible Layout)
- Phase 2: ⏳ Pending (Teacher Portal + Audio Pipeline)
- Phase 3: ⏳ Pending (Student Login + Library)
- Phase 4: ⏳ Pending (Notes Editor + Playback)
- Phase 5: ⏳ Pending (Packaging + Central Server)

## Configuration

Edit the `.env` file to configure:

- `FLASK_APP` - Flask application module (default: `app`)
- `FLASK_ENV` - Environment mode (default: `development`)
- `SECRET_KEY` - Flask secret key (change in production)
- `DB_PATH` - Database file path (default: `instance/shruti.db`)
- `UPLOAD_FOLDER` - PDF upload folder (default: `instance/uploads`)
- `AUDIO_FOLDER` - Generated audio folder (default: `instance/audio`)

## Accessibility Features

Shruti is designed for blind students using NVDA screen reader:

- **Skip Link**: Press Up Arrow at page top to skip navigation
- **ARIA Live Regions**: Screen reader announces dynamic content updates
- **Keyboard Navigation**: All features accessible via keyboard only
- **Large Fonts**: Base font size 24px for easy reading
- **High Contrast**: Blue header/footer with white text, black text on white background
- **Visible Focus**: 3px blue outline on all interactive elements
- **Semantic HTML**: Proper heading structure and landmarks

## Development Notes

### Running in Development Mode

The app runs in debug mode by default. Changes to Python files will auto-reload.

### Voice Verification

Run the voice verification script to check available SAPI5 voices:
```bash
python scripts/verify_voices.py
```

This is required before Phase 2 to ensure Hindi voice support is available.

### Database

The database is created automatically on first run. The schema is in `db/schema.sql`.

- Location: `instance/shruti.db`
- Tables: 9 tables with UUID primary keys
- Relationships: Enforced in Python (not SQLite constraints)

## How It Works (Phase 1)

1. User opens the application → sees class picker screen
2. User can navigate class buttons with keyboard (not functional yet)
3. Database is automatically created with full schema
4. Accessibility features (skip link, ARIA, keyboard nav) are active

## Roadmap

- Phase 1: ✅ Skeleton + Database + Base Accessible Layout
- Phase 2: ⏳ Teacher Portal + Audio Pipeline
- Phase 3: ⏳ Student Login + Library
- Phase 4: ⏳ Notes Editor + Playback
- Phase 5: ⏳ Packaging + Central Server
