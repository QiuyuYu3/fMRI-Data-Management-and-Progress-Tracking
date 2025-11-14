from database.base import DatabaseBase
from typing import List, Dict

class AuditOperations(DatabaseBase):
    """Audit log and note template operations"""
    
    def add_note_template(self, name: str, content: str, category: str = "general"):
        """Add note template"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO note_templates (template_name, template_content, category)
            VALUES (?, ?, ?)
        """, (name, content, category))
        self.conn.commit()
    
    def get_note_templates(self) -> List[Dict]:
        """Get all note templates"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM note_templates ORDER BY category, template_name")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
