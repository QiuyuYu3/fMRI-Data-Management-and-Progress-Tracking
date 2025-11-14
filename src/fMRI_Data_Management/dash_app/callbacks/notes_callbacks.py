from dash import callback, Output, Input, State, callback_context, dash
import dash_bootstrap_components as dbc

def register_notes_callbacks(app, db):
    """Register notes editor callbacks"""
    
    @app.callback(
        [Output('notes-editor-modal', 'is_open'),
         Output('notes-editor-textarea', 'value'),
         Output('notes-edit-context', 'data')],
        [Input('data-table', 'active_cell'),
         Input('cancel-notes-edit', 'n_clicks'),
         Input('save-notes-edit', 'n_clicks')],
        [State('notes-editor-textarea', 'value'),
         State('notes-edit-context', 'data'),
         State('data-table', 'derived_virtual_data'),
         State('data-table', 'page_current'),
         State('data-table', 'page_size'),
         State('current-table', 'data')],
        prevent_initial_call=True
    )
    def manage_notes_editor(active_cell, cancel_clicks, save_clicks,
                           notes_value, context, derived_data,
                           page_current, page_size, current_table):
        ctx = callback_context
        if not ctx.triggered:
            return False, "", None
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Close modal
        if trigger_id in ['cancel-notes-edit', 'save-notes-edit']:
            if trigger_id == 'save-notes-edit' and context:
                # Save notes to database
                if current_table == 'qc_data':
                    db.update_field(
                        context['subject_id'], 
                        context['wave'], 
                        'notes', 
                        notes_value, 
                        user='dash_user'
                    )
                else:
                    row_id = context.get('row_id')
                    if row_id:
                        db.update_secondary_table_field_by_rowid(
                            current_table, row_id, 'notes', notes_value, user='dash_user'
                        )
            return False, "", None
        
        # Open modal when clicking notes cell
        if trigger_id == 'data-table' and active_cell:
            if active_cell.get('column_id') == 'notes':
                row_index = active_cell['row']
                page_current = page_current or 0
                page_size = page_size or 25
                actual_index = page_current * page_size + row_index
                
                if not derived_data or actual_index >= len(derived_data):
                    return False, "", None
                
                row_data = derived_data[actual_index]
                subject_id = str(row_data.get('ID'))
                wave = str(row_data.get('wave', ''))
                current_notes = row_data.get('notes', '') or ''
                
                context = {
                    'subject_id': subject_id,
                    'wave': wave,
                    'row_id': row_data.get('row_id')
                }
                
                return True, current_notes, context
        
        return False, "", None