# SQL Schema Definitions
SQL_SCHEMAS = {
    'qc_data': """
        CREATE TABLE IF NOT EXISTS qc_data (
            ID TEXT NOT NULL,
            wave TEXT NOT NULL,
            qc_metrics TEXT,
            rescan INTEGER DEFAULT 0,
            tags TEXT,
            notes TEXT,
            PPG TEXT,
            PPG_correct TEXT,
            cglab TEXT,
            projects TEXT,
            Download TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT,
            PRIMARY KEY (ID, wave)
        )
    """,
    
    'column_config': """
        CREATE TABLE IF NOT EXISTS column_config (
            column_key TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            data_type TEXT DEFAULT 'text',
            valid_values TEXT,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'audit_log': """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id TEXT NOT NULL,
            wave TEXT NOT NULL,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            action_type TEXT,
            updated_by TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'note_templates': """
        CREATE TABLE IF NOT EXISTS note_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT NOT NULL,
            template_content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'table_registry': """
        CREATE TABLE IF NOT EXISTS table_registry (
            table_name TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            description TEXT,
            primary_keys TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            is_primary INTEGER DEFAULT 0
        )
    """
}

# Registry Initial Data
REGISTRY_INITIAL_DATA = {
    'table_name': 'qc_data',
    'display_name': 'QC Data',
    'primary_keys': '["ID", "wave"]',
    'is_primary': 1,
    'created_by': 'system'
}

