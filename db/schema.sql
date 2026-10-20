-- Shruti Database Schema
-- All primary keys use UUID v4 (TEXT type)
-- Relationships enforced in Python (sqlite3 FK constraints require PRAGMA)

-- Classes (e.g., "Class 10 — Vocational")
CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_order INTEGER,
    created_at TEXT NOT NULL
);

-- Students (each student belongs to exactly one class)
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_id TEXT,
    display_order INTEGER,
    created_at TEXT NOT NULL
);

-- Subjects (shared across classes, e.g., "English", "Hindi", "Math")
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_order INTEGER,
    created_at TEXT NOT NULL
);

-- Lessons (main lesson entity)
CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    class_id TEXT,
    subject_id TEXT,
    pdf_filename TEXT NOT NULL,
    extracted_text TEXT,
    language TEXT NOT NULL,
    scanned_pdf INTEGER DEFAULT 0,
    page_count INTEGER,
    audio_status TEXT DEFAULT 'pending',
    job_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Lesson versions (for future second-language PDF support)
CREATE TABLE IF NOT EXISTS lesson_versions (
    id TEXT PRIMARY KEY,
    lesson_id TEXT,
    language TEXT NOT NULL,
    pdf_filename TEXT NOT NULL,
    page_count INTEGER,
    audio_status TEXT DEFAULT 'pending',
    job_id TEXT,
    created_at TEXT NOT NULL
);

-- Lesson audio files (one row per page per language)
CREATE TABLE IF NOT EXISTS lesson_audio_files (
    id TEXT PRIMARY KEY,
    lesson_id TEXT,
    page_number INTEGER NOT NULL,
    language TEXT NOT NULL,
    audio_filename TEXT NOT NULL,
    duration_seconds REAL,
    created_at TEXT NOT NULL
);

-- Notes (student notes per subject)
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    student_id TEXT,
    subject_id TEXT,
    title TEXT NOT NULL,
    content TEXT,
    audio_filename TEXT,
    audio_status TEXT DEFAULT 'pending',
    job_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Generation jobs (background audio generation progress tracking)
CREATE TABLE IF NOT EXISTS generation_jobs (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    status TEXT DEFAULT 'queued',
    progress_current INTEGER DEFAULT 0,
    progress_total INTEGER DEFAULT 0,
    progress_message TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    error_message TEXT
);

-- App configuration (PIN hash, voice verification status, etc.)
CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,
    value TEXT
);
