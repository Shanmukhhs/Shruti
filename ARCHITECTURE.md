# Shruti — Architecture Document

> **Project:** Shruti — Offline, audio-first learning web app for blind students  
> **Platform:** Windows + NVDA, no internet  
> **Tech Stack:** Python/Flask, SQLite, pdfplumber, pyttsx3 (SAPI5), vanilla HTML/CSS/JS  
> **Last Updated:** 2026-10-15  
> **Status:** **APPROVED PLAN** — ready for Phase 1 implementation

---

## 0. Decisions Made in This Session

| Q  | Decision | Rationale |
|----|----------|-----------|
| Q11 | Allow any PDF size with live NVDA progress | Students/teachers need to know it's working, not frozen |
| Q12 | One audio file per PDF page (per language) | Page-level jump > constant rewinding on 30-page lessons |
| Q13 | One audio file per entire note | Notes are shorter; simpler player reuse |
| Q14 | Background thread worker + queue + DB progress | pyttsx3 blocks; Flask must return immediately to browser |
| Q15 | UUID for every database primary key | Future-proof for Central Server or distributed sync |
| Q16 | Always show class screen (even one class) | Consistent flow, muscle memory for blind users |
| Q17 | WAV only (pyttsx3 SAPI5 default) | No converter dependency; browsers play WAV natively |
| Q18 | Reject if >50% of pages have <50 extractable chars | Reliable scanned-PDF detection |

---

## 1. Folder Structure

```
D:\Shruti\
├── app/                        # Flask application package
│   ├── __init__.py             # App factory, DB init, config
│   ├── routes_student.py       # Student-facing routes (/, /lesson/<id>, /notes)
│   ├── routes_teacher.py       # Teacher routes (/teacher/*, PIN-protected)
│   ├── routes_api.py           # AJAX endpoints (/api/job/<id>/progress)
│   ├── pdf_processor.py        # pdfplumber extract + script detection + scanned rejection
│   ├── tts_engine.py           # pyttsx3 wrapper: voice init, language routing
│   ├── audio_worker.py         # Background thread: reads queue, generates audio, updates progress
│   ├── db.py                   # sqlite3 helpers, UUID generation
│   ├── models.py               # Data classes (UUIDs, validation, relationships)
│   └── utils.py                # Slugify, sanitize, file paths, constants
├── instance/                    # NOT tracked in git; created at runtime
│   ├── shruti.db               # Single SQLite file (path configurable)
│   ├── uploads/                # Teacher-uploaded PDFs
│   └── audio/                  # Generated WAV files
├── templates/                  # Jinja2 templates (vanilla HTML, semantic)
│   ├── base.html               # Shared layout
│   ├── student/
│   │   ├── index.html          # Class picker
│   │   ├── students.html       # Name picker
│   │   ├── dashboard.html      # Lesson list + notes link
│   │   ├── lesson.html         # Page-list audio players + text
│   │   ├── notes.html          # List of notes
│   │   └── note.html           # Edit note (textarea) + play
│   └── teacher/
│       ├── pin.html            # PIN entry
│       ├── dashboard.html      # Upload, Manage links
│       ├── upload.html         # Upload form
│       ├── lesson_form.html    # Edit lesson
│       └── manage.html         # CRUD classes/students/subjects
├── static/
│   ├── css/
│   │   └── shruti.css          # High-contrast, 24px+, focus outlines
│   ├── js/
│   │   ├── audio-player.js     # HTML5 audio controls
│   │   ├── progress-poll.js    # Polls progress, updates live region
│   │   └── form-utils.js       # Auto-save notes
│   └── img/
├── scripts/
│   └── verify_voices.py        # ONE-TIME: check SAPI5 Hindi voice exists
├── tests/
│   ├── test_pdf_processor.py
│   ├── test_tts_engine.py
│   └── test_db.py
├── start_shruti.bat            # One-click launcher (Phase 5)

> **Note:** `instance/` and `audio/` are **large** and **regenerable** — never in git.  
> `requirements.txt`: `flask==3.x`, `pyttsx3==2.90`, `pdfplumber==0.x` (see Phase 1).

---

## 2. Database Schema

> **Primary key strategy:** `TEXT` UUID everywhere. Display order uses `_created_at` or `_sort_order` columns.  
> **Relationships enforced in Python** (sqlite3 doesn't do FK constraints reliably without `PRAGMA foreign_keys = ON`).

### 2.1 `students`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `name` | TEXT | NOT NULL | Full name as it appears on roster |
| `class_id` | TEXT | FK→classes.id | Each student in exactly one class |
| `display_order` | INTEGER | — | Sort order for name-picker grid |
| `created_at` | TEXT | NOT NULL | ISO-8601 UTC timestamp |

### 2.2 `classes`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `name` | TEXT | NOT NULL, UNIQUE | E.g., "Class 10 — Vocational" |
| `display_order` | INTEGER | — | Sort order for class-picker grid |
| `created_at` | TEXT | NOT NULL | |

### 2.3 `subjects`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `name` | TEXT | NOT NULL, UNIQUE | Shared across classes. E.g., "English", "Hindi", "Math" |
| `display_order` | INTEGER | — | |
| `created_at` | TEXT | NOT NULL | |

### 2.4 `lessons`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `title` | TEXT | NOT NULL | Teacher sets on upload |
| `class_id` | TEXT | FK→classes.id | Lesson belongs to one class |
| `subject_id` | TEXT | FK→subjects.id | Lesson belongs to one subject |
| `pdf_filename` | TEXT | NOT NULL | Stored in instance/uploads/ |
| `extracted_text` | TEXT | — | Full extracted text (teacher review + display) |
| `language` | TEXT | NOT NULL | `"english"`, `"hindi"`, or `"mixed"` |
| `scanned_pdf` | INTEGER | DEFAULT 0 | 1 = rejected scanned PDF |
| `page_count` | INTEGER | — | Number of pages in PDF |
| `audio_status` | TEXT | DEFAULT "pending" | `"pending"`, `"partial"`, `"done"`, `"failed"` |
| `job_id` | TEXT | FK→generation_jobs.id | Last generation job |
| `created_at` | TEXT | NOT NULL | Used for "newest first" |
| `updated_at` | TEXT | NOT NULL | On replace/update |

> **Future: Second-language version** → see `lesson_versions` (Section 2.5).

### 2.5 `lesson_versions` (for future second-language PDF)

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `lesson_id` | TEXT | FK→lessons.id | Parent lesson |
| `language` | TEXT | NOT NULL | `"english"` or `"hindi"` |
| `pdf_filename` | TEXT | NOT NULL | This version's PDF |
| `page_count` | INTEGER | — | |
| `audio_status` | TEXT | DEFAULT "pending" | |
| `job_id` | TEXT | FK→generation_jobs.id | |
| `created_at` | TEXT | NOT NULL | |

> **Design rationale:** `lessons` holds the main entity (title, class, subject). `lesson_versions` holds language-specific PDFs and audio. First PDF → one version. Second-language PDF later → second version. **Zero schema rewrite.**

### 2.6 `lesson_audio_files`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `lesson_id` | TEXT | FK→lessons.id | Which lesson |
| `page_number` | INTEGER | NOT NULL | 1-based page number |
| `language` | TEXT | NOT NULL | `"english"` or `"hindi"` |
| `audio_filename` | TEXT | NOT NULL | WAV file in instance/audio/ |
| `duration_seconds` | REAL | — | Set after generation |
| `created_at` | TEXT | NOT NULL | |

> One row per page per language. 30-page mixed PDF → up to 60 rows.  
> **Index needed:** `(lesson_id, page_number, language)` for fast page-list generation.

### 2.7 `notes`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `student_id` | TEXT | FK→students.id | Who owns this note |
| `subject_id` | TEXT | FK→subjects.id | Which subject |
| `title` | TEXT | NOT NULL | E.g., "Algebra Formulas" |
| `content` | TEXT | — | The note text from `<textarea>` |
| `audio_filename` | TEXT | — | WAV file for this note (one per note) |
| `audio_status` | TEXT | DEFAULT "pending" | `"pending"`, `"done"`, `"failed"` |
| `job_id` | TEXT | FK→generation_jobs.id | |
| `created_at` | TEXT | NOT NULL | Newest first |
| `updated_at` | TEXT | NOT NULL | On edit |

### 2.8 `generation_jobs`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `id` | TEXT | PK | UUID v4 |
| `entity_type` | TEXT | NOT NULL | `"lesson"` or `"note"` |
| `entity_id` | TEXT | NOT NULL | UUID of lesson or note |
| `status` | TEXT | DEFAULT "queued" | `"queued"`, `"running"`, `"done"`, `"failed"` |
| `progress_current` | INTEGER | DEFAULT 0 | e.g., page 12 |
| `progress_total` | INTEGER | DEFAULT 0 | e.g., 50 |
| `progress_message` | TEXT | — | e.g., "Page 12 of 50" |
| `created_at` | TEXT | NOT NULL | |
| `started_at` | TEXT | — | |
| `finished_at` | TEXT | — | |
| `error_message` | TEXT | — | If failed |

> **Progress polling:** Frontend calls `/api/job/<id>/progress` → returns JSON `{current, total, message, status}`.  
> **ARIA live region:** `progress-poll.js` writes "Creating audio, page 12 of 50" to live region.

### 2.9 `app_config`

| Column | Type | Constraint | Notes |
|--------|------|------------|-------|
| `key` | TEXT | PK | e.g., `"teacher_pin_hash"`, `"hindi_voice_verified"` |
| `value` | TEXT | — | e.g., SHA-256 hash, `"true"` |

> Initialized during Phase 5 setup. `teacher_pin_hash` = SHA-256 of PIN (never plaintext).

---

## 3. PDF → Text → Audio Pipeline

### 3.1 Upload Flow (Teacher side, behind PIN)

```
1. Teacher clicks "Upload Lesson" → upload.html form
2. Selects PDF file, class, subject, optional title
3. Clicks "Upload" → POST /teacher/upload
4. Flask saves PDF to instance/uploads/<uuid>.pdf
5. pdfplumber extracts text + checks for scanned PDF
6. If scanned → reject, flash message
7. If OK → determine language(s) → create lesson row + enqueue job
8. Redirect to progress page → worker generates audio in background
```

### 3.2 Scanned-PDF Rejection (Q18-A)

```python
# pdf_processor.py — pseudocode
def is_scanned_pdf(pdf_path):
    text_page_count = 0
    total_pages = len(pdf.pages)
    for page in pdf.pages:
        text = page.extract_text() or ""
        if len(text.strip()) >= 50:
            text_page_count += 1
    # Reject if >50% of pages have no readable text
    return (text_page_count / total_pages) < 0.5
```

> **Threshold:** < 50 chars on > 50% of pages → scanned = reject.  
> **Teacher sees:** extracted text preview before confirming.

### 3.3 Script Detection (Locked Decision 8)

```python
# utils.py — uses only stdlib `re`
def detect_language(text):
    devanagari = len(re.findall(r'[\u0900-\u097F]', text))
    latin = len(re.findall(r'[A-Za-z]', text))
    if devanagari > 0 and latin > 0:
        return "mixed"
    elif devanagari > 0:
        return "hindi"
    elif latin > 0:
        return "english"
    else:
        return "english"  # fallback
```

> **Mixed PDF:** Split per page into Hindi runs + English runs. Generate one WAV per page per language. Student sees two player lists.

### 3.4 Background Worker (Q14-A)

```
Thread 1: Flask app (HTTP requests)
Thread 2: Audio worker (daemon, started at app startup)

Queue: Python queue.Queue (thread-safe)

Flow:
1. Upload handler: pdfplumber extract → split pages → push job per page to queue
2. Worker: while True: job = queue.get(); generate_audio(job); queue.task_done()
3. After each page: UPDATE generation_jobs → progress_current, progress_message
4. Frontend: progress-poll.js polls every 2s → updates live region
5. When job.status == "done": frontend hides progress, shows player list
```

> **pyttsx3 safety:** Initialize engine **inside worker thread only**. Use `threading.Lock` around save+runAndWait. Never call from Flask request handler.

### 3.5 Audio File Naming

```
instance/audio/
├── lesson_<lesson_uuid>/
│   ├── page_0001_voice_en.wav
│   ├── page_0002_voice_en.wav
│   ├── page_0001_voice_hi.wav    # if mixed
│   └── page_0003_voice_hi.wav
└── note_<note_uuid>.wav
```

### 3.6 Error Handling

| Scenario | Response |
|----------|----------|
| Scanned PDF detected | Reject at upload, show message |
| No Hindi SAPI5 voice | Block Hindi/mixed upload, show clear instructions |
| pyttsx3 crash | Catch exception, mark job `failed`, log to file |
| Disk full | Catch `OSError`, mark job `failed`, delete partials |
| PDF corrupt | pdfplumber raises error → reject with message |

---

## 4. Screen and Route Map

### 4.1 Student Side

| URL | Template | Purpose |
|-----|----------|---------|
| `/` | `student/index.html` | **Class picker** — large buttons, `<h1>Choose Your Class</h1>` |
| `/student` | `student/students.html` | **Name picker** — filtered by selected class |
| `/dashboard` | `student/dashboard.html` | **Lesson library** — subjects, lessons (newest first) |
| `/lesson/<uuid>` | `student/lesson.html` | **Lesson page** — page-list players + extracted text |
| `/notes` | `student/notes.html` | **Notes list** — titled notes per subject |
| `/note/new?subject=<id>` | `student/note.html` | **Create note** — textarea + label, auto-save |
| `/note/<uuid>` | `student/note.html` | **Edit note** — same form, play + delete |

**Session:** `session['class_id']`, `session['student_id']`.  
**Auto-save:** textarea oninput → debounce 1s → POST `/api/note-save` → "Note saved" in live region.

### 4.2 Teacher Side

| URL | Template | Purpose |
|-----|----------|---------|
| `/teacher` | `teacher/pin.html` | **PIN entry** — `<h1>Teacher Login</h1>` |
| `/teacher/dashboard` | `teacher/dashboard.html` | **Portal** — upload + manage links |
| `/teacher/upload` | `teacher/upload.html` | **Upload form** — PDF + class + subject + title |
| `/teacher/lesson/<uuid>` | `teacher/lesson_form.html` | **Edit lesson** — title, class, subject, delete/replace |
| `/teacher/manage` | `teacher/manage.html` | **CRUD** classes, students, subjects |

**Session:** `session['teacher_authed'] = True` for 8 hours.

---

## 5. NVDA Accessibility Strategy

### 5.1 Base Template — Every Page

```html
<a href="#main" class="skip-link">Skip to main content</a>
<header><h1>{{ page_h1 }}</h1></header>
<main id="main" tabindex="-1">
  {% block content %}{% endblock %}
</main>
<div aria-live="polite" id="aria-live-progress"></div>
<div aria-live="polite" id="aria-live-messages"></div>
<footer>
  <p>Shruti — Offline Audio Learning</p>
</footer>
```

> **Two live regions:** `progress-poll.js` writes to `#aria-live-progress`. All alerts (saved, deleted) go to `#aria-live-messages`.  
> **Focus:** Skip link → first button → Tab order follows DOM.

### 5.2 Per-Screen Requirements

| Screen | H1 Text | Focus Target | Live Region |
|--------|---------|--------------|-------------|
| Class Picker | "Choose Your Class" | First class button | — |
| Name Picker | "Choose Your Name" | Search box or first name | — |
| Dashboard | "Welcome, Priya" | First lesson link | — |
| Lesson Page | "[Lesson Title]" | First page play button | — |
| Notes List | "Your Notes" | First note link | — |
| Note Editor | "Edit Note: [title]" | Textarea | "Note saved" on autosave |
| Upload Form | "Upload Lesson" | PDF input | Progress messages |
| Manage Page | "Manage Classes, Students, Subjects" | First edit field | "Saved" / "Deleted" |

### 5.3 Audio Player (All Screens)

```html
<div class="audio-player" role="region" aria-labelledby="player-title">
  <h2 id="player-title">Page 1 — English</h2>
  <button aria-label="Rewind 30 seconds">⏪ 30s</button>
  <button aria-label="Play">▶</button>
  <button aria-label="Pause">⏸</button>
  <button aria-label="Fast forward 30 seconds">⏭ 30s</button>
  <label for="speed-select">Playback speed</label>
  <select id="speed-select">
    <option value="0.75">0.75x</option>
    <option value="1.0" selected>1x</option>
    <option value="1.25">1.25x</option>
    <option value="1.5">1.5x</option>
  </select>
  <audio src="{{ audio_url }}" preload="none"></audio>
</div>
```

> Every button has `aria-label`. No icon-only controls. `<label>` on every input.

---

## 6. Phased Build Plan

### Phase 1: Skeleton + DB + Base Layout (Week 1)

**Goal:** Empty Flask app that shows a page with `<h1>`, skip link, live region.
SQLite DB created with all tables. Student class picker works.

**Deliverables:**
- [ ] `app/__init__.py` — app factory, DB init, instance folder creation
- [ ] `app/db.py` — UUID helper, `db_execute()`, `db_query()`
- [ ] `templates/base.html` — skip link, header, main, live regions, footer
- [ ] `static/css/shruti.css` — 24px+, high contrast, focus outlines
- [ ] `student/index.html` + route `/` — class picker
- [ ] `db/schema.sql` — all CREATE TABLE statements (UUID PKs)
- [ ] `scripts/verify_voices.py` — check SAPI5 voices

**Manual Test Checklist:**
- [ ] `python -m app` starts server on `127.0.0.1:5000`
- [ ] Visit `/` — NVDA reads `<h1>Choose Your Class</h1>`
- [ ] Tab to buttons — Enter navigates
- [ ] Up Arrow shows "Skip to main content" link
- [ ] `instance/shruti.db` created, tables exist in sqlite3
- [ ] `scripts/verify_voices.py` runs, shows voice list

---

### Phase 2: Teacher Portal + Audio Pipeline (Weeks 2–3)

**Goal:** Teacher uploads PDF → audio generated in background → student plays per-page audio.

**Deliverables:**
- [ ] `teacher/pin.html` + route `/teacher` — PIN entry
- [ ] `teacher/upload.html` + route `/teacher/upload` — form with class/subject
- [ ] `pdf_processor.py` — extract text, scanned-PDF rejection
- [ ] `tts_engine.py` — pyttsx3 init, Hindi/English voice detection
- [ ] `audio_worker.py` — background thread, queue, progress
- [ ] `routes_api.py` — `/api/job/<id>/progress` polling endpoint
- [ ] `lesson.html` — per-page player list
- [ ] Route `/lesson/<uuid>`

**Manual Test Checklist:**
- [ ] Teacher enters PIN → dashboard loads
- [ ] Upload valid English PDF → progress page shows "Page 1 of N"
- [ ] Audio files generated as WAV in `instance/audio/`
- [ ] Upload scanned PDF → rejected with message
- [ ] Student opens lesson → sees page-list players
- [ ] Press Enter on page → audio plays

---

### Phase 3: Student Login + Library (Week 2)

**Goal:** Passwordless login + dashboard with lesson library.

**Deliverables:**
- [ ] `student/students.html` — name picker filtered by class
- [ ] Session: `session['class_id']`, `session['student_id']`
- [ ] `dashboard.html` — subjects as `<h2>`, lessons (newest first)
- [ ] Manage screen: CRUD classes, students, subjects
- [ ] Subject dropdown on upload uses DB subjects
- [ ] Back button from name picker to class picker

**Manual Test Checklist:**
- [ ] Select class → only students in that class shown
- [ ] Select name → dashboard loads
- [ ] Dashboard shows "Welcome, [Name]" + subjects
- [ ] Lessons sorted newest first
- [ ] "Back to classes" button works
- [ ] Single class → still shows class screen with one button

---

### Phase 4: Notes Editor + Playback (Week 3)

**Goal:** Students create titled notes, auto-save, play as audio.

**Deliverables:**
- [ ] `notes.html` — list notes per subject
- [ ] `note.html` — textarea + label, auto-save via `/api/note-save`
- [ ] Note audio generation (one WAV per note)
- [ ] Reuse `audio-player.js` for note playback
- [ ] Delete note with "Are you sure?" confirmation

**Manual Test Checklist:**
- [ ] Click "New Note" → textarea with label appears
- [ ] Type 5 chars → "Note saved" announced (auto-save)
- [ ] Press "Play note" → audio plays
- [ ] Click "Delete" → confirm dialog → note removed
- [ ] Notes listed newest first, grouped by subject

---

### Phase 5: Packaging + Central Server + USB (Week 4)

**Goal:** One-click launcher, Central Server mode, USB backup.

**Deliverables:**
- [ ] `start_shruti.bat` — launches Flask, opens browser, listens on `0.0.0.0`
- [ ] `.env` / `.env.example` — configurable DB path
- [ ] PIN hashing (SHA-256 via `hashlib`)
- [ ] Hindi voice verification gate
- [ ] USB export/import (backup DB + audio)

**Manual Test Checklist:**
- [ ] Double-click `start_shruti.bat` → server starts, browser opens
- [ ] From another PC: `http://[server-ip]:5000` loads
- [ ] Teacher PIN hashed in DB (no plaintext)
- [ ] No Hindi voice → upload blocked with clear message
- [ ] USB backup → restore on different PC → data persists

---

## 7. Risks and Open Items

### 🔴 CRITICAL: Hindi SAPI5 Voice Verification (BEFORE Phase 2)

**Task:** Run `scripts/verify_voices.py` on actual lab PCs.

**If no Hindi voice found:**
- Block Hindi/mixed PDF uploads
- Show message: "Install a Hindi voice: Windows Settings → Time & Language → Speech → Add Hindi"
- Log to file, not silent fail

### 🟡 pyttsx3 Thread-Safety

**Known pitfall:** pyttsx3 is NOT thread-safe.

**Mitigation:**
- Initialize engine inside worker thread only
- `threading.Lock` around `save_to_file` + `runAndWait`
- If `runAndWait` hangs > 30s → kill job, mark `failed`

### 🟡 Storage Estimate

**WAV format:** PCM 16-bit, 22.05 kHz, mono ≈ 176 KB/min

| Content | Estimate | Total |
|--------|----------|-------|
| 20 lessons × 10 pages × 2 lang × 30s | ~264 KB/page | ~100 MB |
| 30 students × 50 notes × 30s | ~264 KB/note | ~400 MB |
| **Total** | | **~500 MB** |

> Fits easily on Windows SSD.

### 🟡 Mixed-Language Page Splitting

**Approach:** Per page, split into Devanagari runs + Latin runs. Generate separate Hindi and English WAV files. Student sees two player lists.

### 🟡 Devanagari Extraction Quality

**Risk:** pdfplumber may garble Devanagari.

**Mitigation:** Show extracted text to teacher on upload. Log raw bytes. Let teacher reject if garbled.

### 🟢 Deferred (Not Needed for MVP)

- Mobile app
- Lecture recording upload
- OCR for scanned PDFs
- Translation
- Real-time collaborative notes

---

## 8. Key Architecture Decisions (Summary)

| Decision | Choice |
|----------|--------|
| DB primary key | UUID (TEXT, uuid4) |
| Audio generation | Background thread + queue.Queue |
| Audio format | WAV (pyttsx3 SAPI5 default) |
| Lesson audio | Per page, per language |
| Note audio | One per entire note |
| Second-language PDF | `lesson_versions` table (ready) |
| Class screen | Always shown (even 1 class) |
| Scanned PDF | Reject if >50% pages <50 chars |
| Server mode | Central Server (LAN) with UUIDs |
| PIN security | SHA-256 hash in `app_config` |
| Voice gate | `verify_voices.py` before Phase 2 |

---

## 9. Next Steps

1. ✅ **Phase 5 Prerequisite** — Run `scripts/verify_voices.py` on a lab PC.
2. 🚧 **Phase 1** — One focused step at a time. Start with `app/__init__.py`.


```
