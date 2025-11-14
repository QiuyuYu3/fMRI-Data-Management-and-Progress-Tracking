from dash import callback, Output, Input, State, dcc
import pandas as pd
from datetime import datetime
from utils.data_processing import prepare_export_dataframe

def register_export_callbacks(app, db):
    """Register export-related callbacks"""
    
    @app.callback(
        Output('download-csv', 'data'),
        Input('export-all', 'n_clicks'),
        [State('filtered-data', 'data'), State('current-table', 'data')],
        prevent_initial_call=True
    )
    def export_all_data(n_clicks, data, current_table):
        """Export all data from current table"""
        if n_clicks and data:
            df = pd.DataFrame(data)
            is_qc = (current_table == 'qc_data')
            df = prepare_export_dataframe(df, is_qc)
            
            table_name = current_table if current_table else 'qc_data'
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            return dcc.send_data_frame(df.to_csv, filename, index=False)
        return dash.no_update
    
    
    @app.callback(
        Output('download-csv', 'data', allow_duplicate=True),
        Input('export-selected', 'n_clicks'),
        [State('data-table', 'selected_rows'),
         State('data-table', 'data'),
         State('current-table', 'data')],
        prevent_initial_call=True
    )
    def export_selected_data(n_clicks, selected_rows, data, current_table):
        """Export selected rows only"""
        if n_clicks and selected_rows and data:
            selected_data = [data[i] for i in selected_rows]
            df = pd.DataFrame(selected_data)
            is_qc = (current_table == 'qc_data')
            df = prepare_export_dataframe(df, is_qc)
            
            table_name = current_table if current_table else 'qc_data'
            filename = f"{table_name}_selected_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            return dcc.send_data_frame(df.to_csv, filename, index=False)
        return dash.no_update


