from dash import callback, Output, Input, State, html, dash
import dash_bootstrap_components as dbc
from utils.file_operations import decode_uploaded_file, prepare_temp_csv, cleanup_temp_file
from utils.validators import validate_csv_structure, validate_table_name
import pandas as pd
import io


def register_import_callbacks(app, db):
    """Register import-related callbacks"""

    def create_preview_table(df, extra_messages=None):
        """Helper function to create preview table"""
        from dash import dash_table
        
        preview = dash_table.DataTable(
            data=df.head(10).to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'fontSize': '12px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )
        
        components = [
            dbc.Alert(
                f"Found {len(df)} rows with {len(df.columns)} columns", 
                color="success", 
                className='mb-2'
            )
        ]
        
        if extra_messages:
            components.extend(extra_messages)
        
        components.extend([
            html.P("Preview (first 10 rows):", className='fw-bold mb-2'),
            preview
        ])
        
        return html.Div(components)

    def handle_preview(contents, filename, additional_messages=None):
        """Generic preview handler"""
        if contents is None:
            return html.Div("No file selected", className='text-muted'), True, None
        
        success, df, error = decode_uploaded_file(contents)
        if not success:
            return dbc.Alert(f"Error reading CSV: {error}", color="danger"), True, None
        
        is_valid, error_msg = validate_csv_structure(df, ['ID'])
        if not is_valid:
            return dbc.Alert(error_msg, color="danger"), True, None
        
        preview_content = create_preview_table(df, additional_messages)
        return preview_content, False, df.to_json(date_format='iso', orient='split')

    @app.callback(
        [Output('import-preview', 'children'),
         Output('confirm-import', 'disabled'),
         Output('uploaded-csv-data', 'data')],
        Input('upload-csv', 'contents'),
        State('upload-csv', 'filename'),
        prevent_initial_call=True
    )
    def preview_qc_csv(contents, filename):
        """Preview CSV before importing to QC data"""
        return handle_preview(contents, filename)

    @app.callback(
        [Output('import-status', 'children'),
        Output('toast-container', 'children', allow_duplicate=True)],
        Input('confirm-import', 'n_clicks'),
        [State('uploaded-csv-data', 'data'),
        State('import-wave', 'value'),
        State('import-project', 'value')],
        prevent_initial_call=True
    )
    def execute_qc_import(n_clicks, csv_data, wave, project):
        """Execute QC data CSV import"""
        if not n_clicks:
            return dash.no_update, dash.no_update
        
        if not csv_data:
            return dbc.Alert("Please upload a CSV file", color="warning"), None
        
        if not wave:
            return dbc.Alert("Wave is required", color="warning"), None
        
        try:
            df = pd.read_json(io.StringIO(csv_data), orient='split')
            
            if project:
                df['projects'] = project
            
            temp_path = prepare_temp_csv(df)
            
            try:
                count = db.import_from_csv(temp_path, wave=wave, user='dash_user')
                
                toast = dbc.Toast(
                    f"Successfully imported {count} records to {wave}",
                    header="Import Complete",
                    is_open=True,
                    duration=4000,
                    className='bg-success text-white'
                )
                
                return dbc.Alert(f"Successfully imported {count} records", color="success"), toast
                
            finally:
                cleanup_temp_file(temp_path)
            
        except Exception as e:
            return dbc.Alert(f"Import failed: {str(e)}", color="danger"), None

    @app.callback(
        [Output('table-import-preview', 'children'),
         Output('confirm-table-import', 'disabled'),
         Output('uploaded-table-csv-data', 'data')],
        Input('upload-table-csv', 'contents'),
        State('upload-table-csv', 'filename'),
        prevent_initial_call=True
    )
    def preview_table_csv(contents, filename):
        """Preview CSV before importing as new table"""
        from config.constants import TABLE_CONFIG
        
        if contents is None:
            return html.Div("No file selected", className='text-muted'), True, None
        
        success, df, error = decode_uploaded_file(contents)
        if not success:
            return dbc.Alert(f"Error reading CSV: {error}", color="danger"), True, None
        
        is_valid, error_msg = validate_csv_structure(df, ['ID'])
        if not is_valid:
            return dbc.Alert(error_msg, color="danger"), True, None
        
        extra_messages = []
        
        metadata_cols = [col for col in TABLE_CONFIG['metadata_columns'] if col in df.columns]
        if metadata_cols:
            extra_messages.append(
                dbc.Alert(
                    f"Columns {metadata_cols} will be overwritten with system-generated values",
                    color="warning",
                    className="mb-2"
                )
            )
        
        extra_messages.append(
            html.P([
                html.Strong("Note: "), 
                "A unique 'row_id' column will be automatically added to this table."
            ], className="text-info small mb-2")
        )
        
        return handle_preview(contents, filename, extra_messages)

    @app.callback(
        [Output('table-import-status', 'children'),
        Output('toast-container', 'children', allow_duplicate=True)],
        Input('confirm-table-import', 'n_clicks'),
        [State('uploaded-table-csv-data', 'data'),
        State('table-name-input', 'value'),
        State('table-display-name', 'value'),
        State('table-description', 'value'),
        State('table-import-wave', 'value'),
        State('table-import-project', 'value'),
        State('table-import-user', 'value')],
        prevent_initial_call=True
    )
    def execute_table_import(n_clicks, csv_data, table_name, display_name, 
                            description, wave, project, user):
        if not n_clicks:
            return dash.no_update, dash.no_update
        
        if not csv_data or not table_name:
            return dbc.Alert("Please fill in table name and upload CSV", color="warning"), None
        
        if not wave or not project:
            return dbc.Alert("Wave and Project are required", color="warning"), None
        
        is_valid, error_msg = validate_table_name(table_name)
        if not is_valid:
            return dbc.Alert(error_msg, color="danger"), None
        
        try:
            df = pd.read_json(io.StringIO(csv_data), orient='split')
            
            if 'wave' not in df.columns:
                df['wave'] = wave
            if 'projects' not in df.columns:
                df['projects'] = project
            
            result = db.create_table_from_dataframe(
                table_name=table_name,
                df=df,
                display_name=display_name or table_name.replace('_', ' ').title(),
                description=description,
                user=user or 'dash_user',
                overwrite=True
            )
            
            if result['success']:
                toast = dbc.Toast(
                    f"{result['message']} (Wave: {wave}, Project: {project})",
                    header="Table Import Complete",
                    is_open=True,
                    duration=4000,
                    className='bg-success text-white'
                )
                return dbc.Alert(f"{result['message']}", color="success"), toast
            else:
                return dbc.Alert(f"Import failed: {result['message']}", color="danger"), None
            
        except Exception as e:
            return dbc.Alert(f"Import failed: {str(e)}", color="danger"), None