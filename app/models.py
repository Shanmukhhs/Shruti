# Data models for Shruti
# These are simple data classes for type hints and structure
# Full validation and relationships will be added in later phases


class Student:
    def __init__(self, id, name, class_id, display_order=None, created_at=None):
        self.id = id
        self.name = name
        self.class_id = class_id
        self.display_order = display_order
        self.created_at = created_at


class Class:
    def __init__(self, id, name, display_order=None, created_at=None):
        self.id = id
        self.name = name
        self.display_order = display_order
        self.created_at = created_at


class Subject:
    def __init__(self, id, name, display_order=None, created_at=None):
        self.id = id
        self.name = name
        self.display_order = display_order
        self.created_at = created_at


class Lesson:
    def __init__(self, id, title, class_id, subject_id, pdf_filename,
                 extracted_text=None, language=None, scanned_pdf=0,
                 page_count=None, audio_status='pending', job_id=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.class_id = class_id
        self.subject_id = subject_id
        self.pdf_filename = pdf_filename
        self.extracted_text = extracted_text
        self.language = language
        self.scanned_pdf = scanned_pdf
        self.page_count = page_count
        self.audio_status = audio_status
        self.job_id = job_id
        self.created_at = created_at
        self.updated_at = updated_at


class Note:
    def __init__(self, id, student_id, subject_id, title, content=None,
                 audio_filename=None, audio_status='pending', job_id=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.student_id = student_id
        self.subject_id = subject_id
        self.title = title
        self.content = content
        self.audio_filename = audio_filename
        self.audio_status = audio_status
        self.job_id = job_id
        self.created_at = created_at
        self.updated_at = updated_at


class GenerationJob:
    def __init__(self, id, entity_type, entity_id, status='queued',
                 progress_current=0, progress_total=0, progress_message=None,
                 created_at=None, started_at=None, finished_at=None,
                 error_message=None):
        self.id = id
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.status = status
        self.progress_current = progress_current
        self.progress_total = progress_total
        self.progress_message = progress_message
        self.created_at = created_at
        self.started_at = started_at
        self.finished_at = finished_at
        self.error_message = error_message
