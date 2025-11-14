from dash import callback, Output, Input, State, callback_context
import dash_bootstrap_components as dbc
from utils.data_processing import (
    parse_qc_metrics,
    get_all_unique_tags,
    filter_dataframe_by_criteria,
    apply_quick_filter
)
import pandas as pd
import json
from config.constants import DEFAULT_HIDDEN_COLUMNS


def register_filter_callbacks(app, db):
    """Register filter-related callbacks"""
    
    @app.callback(
        [Output('data-table', 'columns'),
         Output('data-table', 'data'),
         Output('data-table', 'page_size'),
         Output('filter-wave', 'options'),
         Output('filter-tags', 'options'),
         Output('filtered-data', 'data'),
         Output('column-selector', 'options'),
         Output('column-selector', 'value'),
         Output('current-table', 'data')],
        [Input('filter-id', 'value'),
         Input('filter-wave', 'value'),
         Input('filter-rescan', 'value'),
         Input('filter-tags', 'value'),
         Input('filter-notes', 'value'),
         Input('quick-rescan', 'n_clicks'),
         Input('quick-notes', 'n_clicks'),
         Input('quick-week', 'n_clicks'),
         Input('quick-need_rerun', 'n_clicks'),
         Input('column-selector', 'value'),
         Input('add-subject-modal', 'is_open'),
         Input('toast-container', 'children'),
         Input('table-selector', 'value')],
        #  Input('data-table', 'page_size')],
        State('data-table', 'page_size')
    )
    def update_table(filter_id, filter_wave, filter_rescan, filter_tags, filter_notes,
                    q_rescan, q_notes, q_week, q_need_rerun,
                    hidden_cols, modal_open, toast_children, selected_table, 
                    current_page_size):
        """Update data table with filters and column visibility"""
        
        page_size = current_page_size if current_page_size else 25
        
        if not selected_table:
            selected_table = 'qc_data'
        
        try:
            table_info = db.get_table_info(selected_table)
            if not table_info:
                selected_table = 'qc_data'
        except Exception:
            selected_table = 'qc_data'
        
        if selected_table == 'qc_data':
            raw_data = db.get_all_data_raw()
            df = parse_qc_metrics(raw_data)
        else:
            raw_data = db.get_table_data(selected_table)
            df = pd.DataFrame(raw_data)
            if 'tags' in df.columns:
                df['tags'] = df['tags'].apply(
                    lambda x: ', '.join(json.loads(x)) if x and x != 'null' else ''
                )
        
        if df.empty:
            return [], [], page_size, [], [], [], [], [], selected_table
        
        # Apply filters for qc_data
        if selected_table == 'qc_data':
            ctx = callback_context
            if ctx.triggered:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if button_id.startswith('quick-'):
                    filter_type = button_id.replace('quick-', '')
                    df = apply_quick_filter(df, filter_type)
            
            df = filter_dataframe_by_criteria(
                df, filter_id, filter_wave, filter_rescan,
                filter_tags, filter_notes
            )
        
        # Get wave options
        wave_options = []
        if 'wave' in df.columns:
            wave_options = [{'label': w, 'value': w} for w in sorted(df['wave'].unique())]
        
        # Get tag options
        tag_options = []
        if selected_table == 'qc_data':
            all_tags = get_all_unique_tags(df)
            tag_options = [{'label': t, 'value': t} for t in all_tags]
        
        df['view_details'] = '🔎'
        
        # Column selector options
        all_columns = df.columns.tolist()
        col_options = [{'label': col, 'value': col} 
                    for col in all_columns if col != 'view_details']
        
        if not hidden_cols:
            hidden_cols = DEFAULT_HIDDEN_COLUMNS
        
        # Build visible columns list
        visible_columns = [col for col in all_columns if col not in hidden_cols]
        if 'view_details' in visible_columns:
            visible_columns.remove('view_details')
        visible_columns = ['view_details'] + visible_columns
        
        from config.constants import TABLE_CONFIG
        non_editable = TABLE_CONFIG['non_editable_columns']
        
        # Build column definitions
        columns = [
            {
                'name': 'View' if col == 'view_details' else col,
                'id': col,
                'editable': col not in non_editable,
                'presentation': 'markdown' if col == 'view_details' else None
            }
            for col in visible_columns
        ]
        
        # Ensure ID and wave are in the data (even if hidden from view)
        data_columns = visible_columns.copy()
        if 'ID' not in data_columns:
            data_columns.append('ID')
        if 'wave' not in data_columns:
            data_columns.append('wave')
        
        data = df[data_columns].to_dict('records')
        
        return (columns, data, page_size, wave_options, tag_options,
                df.to_dict('records'), col_options, hidden_cols, selected_table)
    
    
    @app.callback(
        Output('table-selector', 'options'),
        Input('import-table-modal', 'is_open')
    )
    def update_table_selector_options(_):
        """Update table selector dropdown options"""
        tables = db.get_all_tables()
        
        valid_options = []
        for t in tables:
            if not t.get('display_name') or not t.get('table_name'):
                continue
            
            # Verify table exists
            try:
                import sqlite3
                conn = sqlite3.connect(db.db_path)
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (t['table_name'],)
                )
                if cur.fetchone():
                    valid_options.append({
                        'label': t['display_name'],
                        'value': t['table_name']
                    })
                cur.close()
                conn.close()
            except Exception:
                continue
        
        return valid_options
    
    
    @app.callback(
        Output('table-title', 'children'),
        Input('table-selector', 'value')
    )
    def update_table_title(table_name):
        """Update table title based on selected table"""
        if not table_name:
            return "QC Data Table"
        
        table_info = db.get_table_info(table_name)
        if table_info:
            return f"{table_info['display_name']} Table"
        return "Data Table"
    
    @app.callback(
        Output('data-table', 'page_size', allow_duplicate=True),
        Input('page-size-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_page_size(page_size):
        """Update table page size from dropdown"""
        return page_size if page_size else 25