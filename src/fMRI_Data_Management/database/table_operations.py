import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from database.base import DatabaseBase
from config.constants import TABLE_CONFIG

#TODO: Optimize the logic for database table operations

class TableOperations(DatabaseBase):
    """Dynamic table management operations"""
    
    def cleanup_registry(self):
        """Remove orphaned entries from table_registry"""
        self.cursor.execute("SELECT table_name FROM table_registry")
        registered_tables = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [row[0] for row in self.cursor.fetchall()]
        
        orphaned = set(registered_tables) - set(actual_tables)
        for table_name in orphaned:
            if table_name != 'qc_data':
                print(f"[INFO] Removing orphaned registry entry: {table_name}")
                self.cursor.execute("DELETE FROM table_registry WHERE table_name = ?", (table_name,))
        
        self.conn.commit()
        return len(orphaned)
    
    def get_all_tables(self) -> List[Dict]:
        """Get all registered tables that actually exist"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM table_registry ORDER BY is_primary DESC, created_at")
            registered_tables = [dict(row) for row in cur.fetchall()]
            
            valid_tables = []
            for table_info in registered_tables:
                table_name = table_info.get('table_name')
                if not table_name:
                    continue
                
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                    (table_name,)
                )
                
                if cur.fetchone():
                    valid_tables.append(table_info)
                else:
                    print(f"[WARNING] Removing orphaned registry entry: {table_name}")
                    cur.execute("DELETE FROM table_registry WHERE table_name = ?", (table_name,))
            
            conn.commit()
            return valid_tables
        finally:
            conn.close()
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Get information about a specific table"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM table_registry WHERE table_name = ?", (table_name,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_table_data(self, table_name: str) -> List[Dict]:
        """Get all data from a specific table"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            
            # Verify table exists
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table_name,)
            )
            
            if not cur.fetchone():
                print(f"[ERROR] Table '{table_name}' does not exist")
                return []
            
            cur.execute(f"SELECT * FROM {table_name}")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_subject_all_tables_data(self, subject_id: str) -> Dict[str, List[Dict]]:
        """Get data for a subject across ALL tables"""
        result = {}
        tables = self.get_all_tables()
        
        for table_info in tables:
            table_name = table_info['table_name']
            
            conn = self.get_connection()
            try:
                cur = conn.cursor()
                query = f"SELECT * FROM {table_name} WHERE ID = ? ORDER BY wave"
                cur.execute(query, (subject_id,))
                rows = cur.fetchall()
                result[table_name] = [dict(row) for row in rows]
            except Exception as e:
                print(f"[WARNING] Error querying table {table_name}: {e}")
                result[table_name] = []
            finally:
                conn.close()
        
        return result
    
    def register_table(self, table_name: str, display_name: str, 
                      primary_keys: List[str], description: str = None, 
                      user: str = "user"):
        """Register a new table in the registry"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO table_registry 
            (table_name, display_name, description, primary_keys, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (table_name, display_name, description, json.dumps(primary_keys), user))
        self.conn.commit()
    
    def delete_table(self, table_name: str):
        """Delete a secondary table"""
        if table_name == 'qc_data':
            raise ValueError("Cannot delete primary QC data table")
        
        try:
            self.cursor.execute("DELETE FROM table_registry WHERE table_name = ?", (table_name,))
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.commit()
            print(f"[INFO] Successfully deleted table: {table_name}")
        except Exception as e:
            print(f"[ERROR] Failed to delete table {table_name}: {e}")
            self.conn.rollback()
            raise
    
    def create_table_from_dataframe(self, table_name: str, df: pd.DataFrame,
                                    primary_keys: List[str] = None,
                                    display_name: str = None,
                                    description: str = None,
                                    user: str = "user",
                                    overwrite: bool = False) -> Dict:
        """Create a new table from DataFrame with auto-increment row_id"""
        if not display_name:
            display_name = table_name.replace('_', ' ').title()
        
        # Check if table exists
        existing_info = self.get_table_info(table_name)
        if existing_info and not overwrite:
            counter = 2
            original_name = table_name
            while existing_info:
                table_name = f"{original_name}_{counter}"
                existing_info = self.get_table_info(table_name)
                counter += 1
            display_name = f"{display_name} ({counter-1})"
        
        if existing_info and overwrite:
            self.delete_table(table_name)
        
        # Ensure required columns
        if 'wave' not in df.columns:
            raise ValueError("DataFrame must contain 'wave' column")
        if 'projects' not in df.columns:
            raise ValueError("DataFrame must contain 'projects' column")
        
        # Remove metadata columns if they exist
        df_cleaned = df.drop(
            columns=[col for col in TABLE_CONFIG['metadata_columns'] if col in df.columns], 
            errors='ignore'
        )
        
        # Build column definitions
        column_defs = ["row_id INTEGER PRIMARY KEY AUTOINCREMENT"]
        
        for col in df_cleaned.columns:
            dtype = df_cleaned[col].dtype
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "REAL"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                sql_type = "TIMESTAMP"
            else:
                sql_type = "TEXT"
            column_defs.append(f"{col} {sql_type}")
        
        # Add metadata columns
        column_defs.extend([
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_by TEXT"
        ])
        
        # Create table
        create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
        self.cursor.execute(create_sql)
        
        # Register table
        self.register_table(table_name, display_name, ['row_id'], description, user)
        
        # Import data
        rows_imported = 0
        for _, row in df_cleaned.iterrows():
            cols = list(df_cleaned.columns)
            placeholders = ', '.join(['?' for _ in cols])
            values = [row[col] for col in cols]
            values.extend([datetime.now(), datetime.now(), user])
            
            insert_sql = f"""
                INSERT INTO {table_name} 
                ({', '.join(cols)}, created_at, updated_at, updated_by)
                VALUES ({placeholders}, ?, ?, ?)
            """
            self.cursor.execute(insert_sql, values)
            rows_imported += 1
        
        self.conn.commit()
        
        return {
            'success': True,
            'message': f"Successfully created table '{table_name}' with {rows_imported} rows",
            'rows_imported': rows_imported,
            'table_name': table_name
        }
    
    def update_secondary_table_field(self, table_name: str, 
                                    subject_id: str, wave: str,
                                    field_name: str, new_value: any,
                                    user: str = "user") -> bool:
        """Update field in secondary table (no audit log)"""
        if table_name == 'qc_data':
            # Use QC operations for main table
            from database.qc_operations import QCOperations
            return QCOperations.update_field(self, subject_id, wave, field_name, new_value, user)
        
        try:
            self.cursor.execute(f"""
                UPDATE {table_name} 
                SET {field_name} = ?, updated_at = ?, updated_by = ?
                WHERE ID = ? AND wave = ?
            """, (new_value, datetime.now(), user, subject_id, wave))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating {table_name}: {e}")
            return False
    
    def export_to_csv(self, output_path: str, subject_ids: List[str] = None, 
                     table_name: str = 'qc_data'):
        """Export table data to CSV"""
        if subject_ids:
            placeholders = ','.join(['?' for _ in subject_ids])
            query = f"SELECT * FROM {table_name} WHERE ID IN ({placeholders})"
            df = pd.read_sql(query, self.conn, params=subject_ids)
        else:
            df = pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
        
        # Process QC data
        if table_name == 'qc_data':
            if 'qc_metrics' in df.columns:
                df['qc_metrics'] = df['qc_metrics'].apply(
                    lambda x: json.loads(x) if x else {}
                )
                qc_df = pd.json_normalize(df['qc_metrics'])
                df = pd.concat([df.drop('qc_metrics', axis=1), qc_df], axis=1)
            
            if 'tags' in df.columns:
                df['tags'] = df['tags'].apply(
                    lambda x: ', '.join(json.loads(x)) if x else ''
                )
        
        df.to_csv(output_path, index=False)
        return len(df)

def update_secondary_table_field_by_rowid(self, table_name: str, 
                                          row_id: int,
                                          field_name: str, new_value: any,
                                          user: str = "user") -> bool:
    """Update field in secondary table using row_id (more precise than ID+wave)"""
    if table_name == 'qc_data':
        raise ValueError("Use QCOperations for qc_data table")
    
    try:
        self.cursor.execute(f"""
            UPDATE {table_name} 
            SET {field_name} = ?, updated_at = ?, updated_by = ?
            WHERE row_id = ?
        """, (new_value, datetime.now(), user, row_id))
        self.conn.commit()
        return True
    except Exception as e:
        print(f"Error updating {table_name} row_id={row_id}: {e}")
        return False