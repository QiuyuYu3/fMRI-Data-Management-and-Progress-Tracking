import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.base import DatabaseBase
from config.constants import TABLE_CONFIG

class QCOperations(DatabaseBase):
    
    def _get_qc_record(self, subject_id: str, wave: str) -> Optional[Dict]:
        """Helper: Get QC record (with error handling)"""
        self.cursor.execute(
            "SELECT * FROM qc_data WHERE ID = ? AND wave = ?", 
            (subject_id, wave)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def _update_qc_field(self, subject_id: str, wave: str, 
                        field_name: str, new_value: Any, user: str):
        """Helper: Update single QC field"""
        self.cursor.execute(f"""
            UPDATE qc_data SET {field_name} = ?, updated_at = ?, updated_by = ?
            WHERE ID = ? AND wave = ?
        """, (new_value, datetime.now(), user, subject_id, wave))
    
    def _log_audit(self, subject_id: str, wave: str, field_name: str, 
                  old_value: Any, new_value: Any, action_type: str, user: str):
        """Helper: Create audit log entry"""
        self.cursor.execute("""
            INSERT INTO audit_log 
            (subject_id, wave, field_name, old_value, new_value, action_type, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject_id, wave, field_name, str(old_value), str(new_value), action_type, user))
    
    def add_subject(self, subject_id: str, wave: str, 
                    other_fields: Dict = None, user: str = "user"):
        if not subject_id or not wave:
            raise ValueError("Subject ID and wave are required")
        
        # Check if exists
        if self._get_qc_record(subject_id, wave):
            raise ValueError(f"Subject {subject_id} wave {wave} already exists")
        
        # Prepare data
        qc_metrics = {}
        fixed_fields = {key: None for key in TABLE_CONFIG['fixed_qc_fields']}
        fixed_fields['rescan'] = 0
        
        if other_fields:
            # Separate QC metrics from fixed fields
            for k, v in other_fields.items():
                if k in TABLE_CONFIG['fixed_qc_fields'] or k in ['ID', 'wave']:
                    fixed_fields[k] = v
                else:
                    qc_metrics[k] = v
            
            # Handle tags
            if 'tags' in fixed_fields:
                tags_str = fixed_fields['tags']
                if tags_str:
                    from utils.data_processing import tags_to_json
                    fixed_fields['tags'] = tags_to_json(tags_str)
        
        # Insert
        self.cursor.execute("""
            INSERT INTO qc_data 
            (ID, wave, qc_metrics, notes, rescan, tags,
             PPG, PPG_correct, cglab, projects, Download, 
             created_at, updated_at, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subject_id, wave, 
            json.dumps(qc_metrics, ensure_ascii=False),
            fixed_fields.get('notes'),
            fixed_fields.get('rescan', 0),
            fixed_fields.get('tags'),
            fixed_fields.get('PPG'),
            fixed_fields.get('PPG_correct'),
            fixed_fields.get('cglab'),
            fixed_fields.get('projects'),
            fixed_fields.get('Download'),
            datetime.now(), datetime.now(), user
        ))
        
        self._log_audit(subject_id, wave, 'new_subject', None, 'created', 'insert', user)
        self.conn.commit()
        return True
    
    def update_field(self, subject_id: str, wave: str, field_name: str, 
                     new_value: Any, user: str = "user"):
        """Update field in qc_data (with audit log)"""
        record = self._get_qc_record(subject_id, wave)
        if not record:
            return False
        
        updatable_fixed_fields = ['notes', 'rescan', 'PPG', 'PPG_correct', 
                                 'cglab', 'projects', 'Download']
        
        # Handle tags
        if field_name == 'tags':
            from utils.data_processing import tags_to_json, extract_tags_from_string
            old_tags = json.loads(record['tags'] or '[]')
            old_value = ', '.join(old_tags)
            
            new_tags_json = tags_to_json(new_value)
            self._update_qc_field(subject_id, wave, 'tags', new_tags_json, user)
            
            new_tags_list = extract_tags_from_string(new_value)
            new_value_str = ', '.join(new_tags_list)
        
        # Handle fixed fields
        elif field_name in updatable_fixed_fields:
            old_value = record[field_name]
            self._update_qc_field(subject_id, wave, field_name, new_value, user)
            new_value_str = str(new_value)
        
        # Handle QC metrics
        else:
            data = json.loads(record['qc_metrics'] or '{}')
            old_value = data.get(field_name)
            data[field_name] = new_value
            
            self._update_qc_field(
                subject_id, wave, 'qc_metrics', 
                json.dumps(data, ensure_ascii=False), user
            )
            new_value_str = str(new_value)
        
        self._log_audit(subject_id, wave, field_name, old_value, new_value_str, 'update', user)
        self.conn.commit()
        return True
    
    def add_tag(self, subject_id: str, wave: str, tag: str, user: str = "user"):
        """Add a single tag to subject"""
        record = self._get_qc_record(subject_id, wave)
        if not record:
            return False
        
        tags = json.loads(record['tags']) if record['tags'] else []
        
        if tag not in tags:
            old_value_str = ', '.join(tags)
            tags.append(tag)
            
            new_tags_json = json.dumps(tags)
            self._update_qc_field(subject_id, wave, 'tags', new_tags_json, user)
            
            new_value_str = ', '.join(tags)
            self._log_audit(subject_id, wave, 'tags', old_value_str, new_value_str, 'add_tag', user)
            
            self.conn.commit()
            return True
        
        return False
    
    def remove_tag(self, subject_id: str, wave: str, tag: str, user: str = "user"):
        """Remove specific tag from subject"""
        record = self._get_qc_record(subject_id, wave)
        if not record:
            return False
        
        current_tags = json.loads(record['tags']) if record['tags'] else []
        
        if tag in current_tags:
            current_tags.remove(tag)
            self._update_qc_field(subject_id, wave, 'tags', json.dumps(current_tags), user)
            self.conn.commit()
            return True
        
        return False
    
    def delete_subject(self, subject_id: str, wave: str, user: str = "user"):
        record = self._get_qc_record(subject_id, wave)
        if not record:
            return False
        
        # Log before deletion
        self._log_audit(subject_id, wave, 'delete', str(dict(record)), None, 'delete', user)
        
        # Delete
        self.cursor.execute(
            "DELETE FROM qc_data WHERE ID = ? AND wave = ?", 
            (subject_id, wave)
        )
        
        self.conn.commit()
        return True
    
    def batch_update(self, subject_wave_pairs: List[tuple], 
                    field_name: str, value: Any, user: str = "user"):
        """Batch update multiple subjects"""
        count = 0
        for subject_id, wave in subject_wave_pairs:
            if field_name == 'tag':
                if self.add_tag(subject_id, wave, value, user):
                    count += 1
            elif self.update_field(subject_id, wave, field_name, value, user):
                count += 1
        return count
    
    def import_from_csv(self, csv_path: str, wave: str, user: str = "system"):
        """Import data from CSV file (no overwrite; log conflicts only)"""
        df = pd.read_csv(csv_path)

        if 'ID' not in df.columns:
            raise ValueError("CSV must contain 'ID' column")

        fixed_columns = TABLE_CONFIG['fixed_qc_fields']
        qc_columns = [col for col in df.columns 
                    if col not in ['ID', 'wave'] + fixed_columns 
                    and not col.startswith('Note') and col != 'notes']

        for col in qc_columns:
            self._register_column(col, col.replace('_', ' ').title())

        imported_count = 0
        conflict_count = 0

        for _, row in df.iterrows():
            subject_id = row['ID']
            existing = self._get_qc_record(subject_id, wave)

            qc_metrics = {col: row[col] for col in qc_columns if pd.notna(row.get(col))}
            notes = '\n'.join([f"{col}: {row[col]}" for col in df.columns 
                            if col.startswith('Note') and pd.notna(row.get(col))])
            notes = notes or row.get('notes')

            from utils.data_processing import tags_to_json
            tags_json = tags_to_json(row['tags']) if pd.notna(row.get('tags')) else None

            if existing:
                existing_metrics = json.loads(existing.get('qc_metrics') or '{}')
                has_conflict = False

                for k, v in qc_metrics.items():
                    old_v = existing_metrics.get(k)
                    if old_v != v:
                        self._log_audit(subject_id, wave, k, old_v, v, 'import_conflict', user)
                        has_conflict = True

                # compare fixed fields too
                for field in ['PPG', 'PPG_correct', 'cglab', 'projects', 'Download', 'rescan', 'notes', 'tags']:
                    new_v = row.get(field)
                    old_v = existing.get(field)
                    if pd.notna(new_v) and str(new_v) != str(old_v):
                        self._log_audit(subject_id, wave, field, old_v, new_v, 'import_conflict', user)
                        has_conflict = True

                if has_conflict:
                    conflict_count += 1
                continue  # skip updating

            # insert new record
            self.cursor.execute("""
                INSERT INTO qc_data 
                (ID, wave, qc_metrics, notes, tags,
                PPG, PPG_correct, cglab, projects, Download, rescan,
                created_at, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                subject_id, wave,
                json.dumps(qc_metrics, ensure_ascii=False),
                notes, tags_json,
                row.get('PPG'), row.get('PPG_correct'),
                row.get('cglab'), row.get('projects'),
                row.get('Download'), row.get('rescan', 0),
                datetime.now(), datetime.now(), user
            ))
            self._log_audit(subject_id, wave, 'qc_import',
                            None, json.dumps(qc_metrics, ensure_ascii=False),
                            'import_insert', user)
            imported_count += 1

        self.conn.commit()
        print(f"Import complete: {imported_count} new rows, {conflict_count} conflicts logged.")
        return imported_count

    
    def _register_column(self, column_key: str, display_name: str = None,
                        data_type: str = 'text', valid_values: List = None):
        """Register new QC metric column"""
        if display_name is None:
            display_name = column_key
        
        self.cursor.execute("""
            INSERT OR IGNORE INTO column_config 
            (column_key, display_name, data_type, valid_values)
            VALUES (?, ?, ?, ?)
        """, (column_key, display_name, data_type, 
              json.dumps(valid_values) if valid_values else None))
        self.conn.commit()
    
    def get_all_data_raw(self):
        """Get all QC data"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM qc_data ORDER BY ID, wave")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_subject_history(self, subject_id: str) -> List[Dict]:
        """Get all waves for a subject"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM qc_data WHERE ID = ? ORDER BY wave
            """, (subject_id,))
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_active_columns(self) -> List[Dict]:
        """Get all active column configurations"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM column_config WHERE is_active = 1 ORDER BY created_at
            """)
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_audit_log(self, subject_id: str = None, limit: int = 100) -> List[Dict]:
        """Get audit log"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if subject_id:
                cur.execute("""
                    SELECT * FROM audit_log 
                    WHERE subject_id = ? 
                    ORDER BY updated_at DESC LIMIT ?
                """, (subject_id, limit))
            else:
                cur.execute("""
                    SELECT * FROM audit_log 
                    ORDER BY updated_at DESC LIMIT ?
                """, (limit,))
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_subject_tags(self, subject_id: str, wave: str) -> List[str]:
        """Get tags for a specific subject"""
        record = self._get_qc_record(subject_id, wave)
        if not record:
            return []
        
        tags_json = record.get('tags')
        if tags_json:
            try:
                return json.loads(tags_json)
            except json.JSONDecodeError:
                return []
        return []





