import pandas as pd
import json
from typing import List, Dict, Any

def parse_qc_metrics(data_list: List[Dict]) -> pd.DataFrame:
    """Expand JSON qc_metrics into columns"""
    df = pd.DataFrame(data_list)
    
    if 'qc_metrics' in df.columns:
        df['qc_metrics'] = df['qc_metrics'].apply(
            lambda x: json.loads(x) if x and x != 'null' else {}
        )
        qc_df = pd.json_normalize(df['qc_metrics'])
        df = pd.concat([df.drop('qc_metrics', axis=1), qc_df], axis=1)
    
    if 'tags' in df.columns:
        df['tags'] = df['tags'].apply(
            lambda x: ', '.join(json.loads(x)) if x and x != 'null' else ''
        )
    
    return df


def extract_tags_from_string(tags_str: str) -> List[str]:
    """Extract tags from comma-separated string"""
    if not tags_str:
        return []
    return [tag.strip() for tag in str(tags_str).split(',') if tag.strip()]


def tags_to_json(tags_input: Any) -> str:
    """Convert various tag inputs to JSON string"""
    if isinstance(tags_input, list):
        return json.dumps(tags_input)
    elif isinstance(tags_input, str):
        tags_list = extract_tags_from_string(tags_input)
        return json.dumps(tags_list)
    return json.dumps([])


def get_all_unique_tags(df: pd.DataFrame) -> List[str]:
    """Extract all unique tags from dataframe"""
    all_tags = set()
    if 'tags' in df.columns:
        for tags_str in df['tags'].dropna():
            if tags_str:
                all_tags.update(extract_tags_from_string(tags_str))
    return sorted(all_tags)


def filter_dataframe_by_criteria(df: pd.DataFrame, 
                                 filter_id: str = None,
                                 filter_wave: str = None,
                                 filter_rescan: str = 'all',
                                 filter_tags: str = None,
                                 filter_notes: str = None,
                                 filter_project: str = None) -> pd.DataFrame:
    """Apply multiple filters to dataframe"""
    if filter_id:
        df = df[df['ID'].str.contains(filter_id, case=False, na=False)]
    
    if filter_wave:
        df = df[df['wave'] == filter_wave]
    
    if filter_rescan and filter_rescan != 'all':
        df = df[df['rescan'] == int(filter_rescan)]
    
    if filter_tags:
        df = df[df['tags'].str.contains(filter_tags, case=False, na=False)]
    
    if filter_notes:
        df = df[df['notes'].str.contains(filter_notes, case=False, na=False)]
    
    if filter_project:
        df = df[df['projects'] == filter_project]
    
    return df


def apply_quick_filter(df, filter_type):
    """Apply quick filter buttons"""
    from datetime import datetime, timedelta
    
    if filter_type == 'rescan':
        return df[df['rescan'] == 1]
    
    elif filter_type == 'notes':
        return df[df['notes'].notna() & (df['notes'] != '')]
    
    elif filter_type == 'need_rerun':
        return df[df['tags'].str.contains('need re-run', case=False, na=False)]
    
    elif filter_type == 'week':
        # Filter subjects created/modified this week
        if 'created_at' not in df.columns:
            return df  # No filtering if no timestamp column
        
        try:
            # Convert to datetime
            df = df.copy()
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            
            # Get start of current week (Monday)
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Filter
            filtered = df[df['created_at'] >= start_of_week]
            print(f"This week filter: {len(filtered)} subjects from {start_of_week.date()}")
            return filtered
            
        except Exception as e:
            print(f"Error in week filter: {e}")
            return df
    
    return df


def prepare_export_dataframe(df: pd.DataFrame, is_qc_data: bool = True) -> pd.DataFrame:
    """Prepare dataframe for CSV export"""
    df = df.copy()
    
    if is_qc_data and 'qc_metrics' in df.columns:
        df['qc_metrics'] = df['qc_metrics'].apply(
            lambda x: json.loads(x) if x and str(x).strip() else {}
        )
        qc_df = pd.json_normalize(df['qc_metrics'])
        df = pd.concat([df.drop('qc_metrics', axis=1), qc_df], axis=1)
    
    if 'tags' in df.columns:
        def safe_parse_tags(x):
            if not x or pd.isna(x) or str(x).strip() == '':
                return ''
            try:
                return ', '.join(json.loads(x))
            except (json.JSONDecodeError, TypeError):
                return str(x)
        
        df['tags'] = df['tags'].apply(safe_parse_tags)
    
    return df