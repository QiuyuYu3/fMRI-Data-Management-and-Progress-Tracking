from database.base import DatabaseBase
from database.qc_operations import QCOperations
from database.table_operations import TableOperations
from database.audit_operations import AuditOperations
from config.constants import DEFAULT_NOTE_TEMPLATES

class FMRIQCDatabase(QCOperations, TableOperations, AuditOperations):
    def __init__(self, db_path: str = "fmri_qc.db"):
        super().__init__(db_path)
        
        # Clean up orphaned registry entries on startup
        try:
            self.cleanup_registry()
        except Exception as e:
            print(f"[WARNING] Failed to cleanup registry: {e}")


def init_default_templates(db: FMRIQCDatabase):
    """Initialize database with default note templates"""
    for name, content, category in DEFAULT_NOTE_TEMPLATES:
        db.add_note_template(name, content, category)


__all__ = [
    'FMRIQCDatabase',
    'init_default_templates',
    'DatabaseBase',
    'QCOperations',
    'TableOperations',
    'AuditOperations'
]






