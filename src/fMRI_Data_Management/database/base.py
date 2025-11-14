import sqlite3
from typing import Optional
from config.constants import DB_CONFIG
from config.database_schema import SQL_SCHEMAS, REGISTRY_INITIAL_DATA

class DatabaseBase:
    """Base database connection and initialization"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_CONFIG['default_path']
        self.conn = sqlite3.connect(
            self.db_path, 
            check_same_thread=DB_CONFIG['check_same_thread']
        )
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._initialize_database()
    
    def _initialize_database(self):
        """Create all database tables"""
        # Create tables
        for table_name, schema_sql in SQL_SCHEMAS.items():
            self.cursor.execute(schema_sql)
        
        # Register qc_data as primary table
        self.cursor.execute("""
            INSERT OR IGNORE INTO table_registry 
            (table_name, display_name, primary_keys, is_primary, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (
            REGISTRY_INITIAL_DATA['table_name'],
            REGISTRY_INITIAL_DATA['display_name'],
            REGISTRY_INITIAL_DATA['primary_keys'],
            REGISTRY_INITIAL_DATA['is_primary'],
            REGISTRY_INITIAL_DATA['created_by']
        ))
        
        self.conn.commit()
    
    def get_connection(self):
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self):
        """Close database connection"""
        self.conn.close()
