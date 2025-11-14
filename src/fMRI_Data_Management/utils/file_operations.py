import base64
import io
import pandas as pd
import tempfile
import os
from typing import Tuple, Optional
from dash import dcc

def decode_uploaded_file(contents: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        return True, df, None
    except Exception as e:
        return False, None, str(e)


def prepare_temp_csv(df: pd.DataFrame) -> str:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name


def cleanup_temp_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"[WARNING] Failed to delete temp file {file_path}: {e}")


def export_dataframe_to_csv(df: pd.DataFrame, filename: str) -> dict:
    return dcc.send_data_frame(df.to_csv, filename, index=False)


def read_csv_safe(file_path: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
    try:
        df = pd.read_csv(file_path)
        return True, df, None
    except Exception as e:
        return False, None, str(e)


