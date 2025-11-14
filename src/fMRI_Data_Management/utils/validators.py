import pandas as pd
from typing import List, Tuple, Optional

def validate_subject_input(subject_id: str, wave: str, project: str) -> Tuple[bool, Optional[str]]:
    if not subject_id:
        return False, "Subject ID is required"
    
    if not wave:
        return False, "Wave is required"
    
    if not project:
        return False, "Project is required"
    
    return True, None


def validate_table_name(table_name: str) -> Tuple[bool, Optional[str]]:
    if not table_name:
        return False, "Table name is required"
    
    # Check for invalid characters
    invalid_chars = [' ', '-', '.', '/', '\\', '(', ')', '[', ']']
    if any(char in table_name for char in invalid_chars):
        return False, "Table name cannot contain spaces or special characters"
    
    # Check for SQL keywords
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'TABLE']
    if table_name.upper() in sql_keywords:
        return False, "Table name cannot be a SQL keyword"
    
    return True, None


def validate_csv_structure(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, Optional[str]]:
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    
    return True, None