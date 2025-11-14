from dash import callback, Output, Input, State
import dash_bootstrap_components as dbc

def register_modal_callbacks(app, db):
    """Register modal toggle callbacks"""
    
    @app.callback(
        Output('add-subject-modal', 'is_open'),
        [Input('add-new-row', 'n_clicks'),
         Input('cancel-add-subject', 'n_clicks'),
         Input('confirm-add-subject', 'n_clicks')],
        [State('add-subject-modal', 'is_open')]
    )
    def toggle_add_subject_modal(n1, n2, n3, is_open):
        """Toggle add subject modal"""
        from dash import callback_context
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'add-new-row' and n1 > 0:
            return True
        
        if trigger_id in ['cancel-add-subject', 'confirm-add-subject']:
            return False
        
        return is_open
    
    
    @app.callback(
        Output('import-modal', 'is_open'),
        [Input('import-csv-btn', 'n_clicks'),
         Input('close-import', 'n_clicks'),
         Input('confirm-import', 'n_clicks')],
        [State('import-modal', 'is_open')]
    )
    def toggle_import_modal(n_open, n_close, n_confirm, is_open):
        """Toggle import CSV modal"""
        if n_open or n_close or n_confirm:
            return not is_open
        return is_open
    
    
    @app.callback(
        Output('import-table-modal', 'is_open'),
        [Input('import-table-btn', 'n_clicks'),
         Input('close-table-import', 'n_clicks'),
         Input('confirm-table-import', 'n_clicks')],
        [State('import-table-modal', 'is_open')]
    )
    def toggle_import_table_modal(n_open, n_close, n_confirm, is_open):
        """Toggle import table modal"""
        if n_open or n_close or n_confirm:
            return not is_open
        return is_open
    
    
    @app.callback(
        Output('add-subject-status', 'children'),
        Input('confirm-add-subject', 'n_clicks'),
        [State('new-subject-id', 'value'),
         State('new-subject-wave', 'value'),
         State('new-subject-project', 'value'),
         State('new-reconstruction', 'value'),
         State('new-t1', 'value'),
         State('new-kidvid', 'value'),
         State('new-k-qc', 'value'),
         State('new-cards', 'value'),
         State('new-c-qc', 'value'),
         State('new-rs', 'value'),
         State('new-r-qc', 'value'),
         State('new-download', 'value'),
         State('new-ppg', 'value'),
         State('new-notes', 'value')],
        prevent_initial_call=True
    )
    def add_new_subject(n_clicks, subject_id, wave, project, reconstruction,
                       t1, kidvid, k_qc, cards, c_qc, rs, r_qc, download, ppg, notes):
        """Add new subject to database"""
        if not n_clicks:
            return ""
        
        from utils.validators import validate_subject_input
        is_valid, error_msg = validate_subject_input(subject_id, wave, project)
        if not is_valid:
            return dbc.Alert(error_msg, color="danger")
        
        try:
            other_fields = {
                'projects': project,
                'reconstruction': reconstruction,
                'T1': t1,
                'kidvid': kidvid,
                'kidvid_QC': k_qc,
                'CARDS': cards,
                'Cards_QC': c_qc,
                'RS': rs,
                'RS_QC': r_qc,
                'Download': download,
                'PPG': ppg,
                'notes': notes
            }
            
            other_fields = {k: v for k, v in other_fields.items() if v is not None}
            
            db.add_subject(subject_id, wave, other_fields, user='dash_user')
            
            return dbc.Alert(
                f"✓ Successfully added {subject_id} ({wave}) to {project}!",
                color="success"
            )
        
        except ValueError as e:
            return dbc.Alert(str(e), color="warning")
        except Exception as e:
            return dbc.Alert(f"Error: {str(e)}", color="danger")
