from dash import callback, Output, Input, State, callback_context, ALL, MATCH, dash
import dash_bootstrap_components as dbc
from dash import html
import json
from datetime import datetime

def register_data_callbacks(app, db):
    """Register data manipulation callbacks"""
    
    @app.callback(
        Output('data-table', 'data', allow_duplicate=True),
        Input('data-table', 'data_timestamp'),
        State('data-table', 'data'),
        State('data-table', 'data_previous'),
        State('data-table', 'derived_virtual_data'),
        State('current-table', 'data'),
        prevent_initial_call=True
    )
    def update_cell(timestamp, current_data, previous_data, derived_data, current_table):
        """Handle cell edits in data table - FIXED for pagination"""
        if not timestamp or not current_data or not current_table:
            return current_data
        
        previous_data = previous_data or []
        
        # Use derived_virtual_data if available (represents displayed data)
        display_data = derived_data if derived_data else current_data
        
        for i, curr_row in enumerate(current_data):
            prev_row = previous_data[i] if i < len(previous_data) else None
            if prev_row:
                for key in curr_row:
                    if key in ['tags', 'view_details']:
                        continue
                    
                    prev_value = prev_row.get(key)
                    
                    if str(curr_row[key]) != str(prev_value):
                        subject_id = curr_row.get('ID')
                        wave = curr_row.get('wave', '')
                        
                        if current_table == 'qc_data':
                            db.update_field(subject_id, wave, key, curr_row[key], user='dash_user')
                        else:
                            # For secondary tables, use row_id if available
                            row_id = curr_row.get('row_id', None)
                            if row_id:
                                db.update_secondary_table_field_by_rowid(
                                    current_table, row_id, key, curr_row[key], user='dash_user'
                                )
                            else:
                                # Fallback to ID+wave
                                db.update_secondary_table_field(
                                    current_table, subject_id, wave, key, curr_row[key], user='dash_user'
                                )
                        
                        return current_data
        
        return current_data
    
    
    @app.callback(
        Output('batch-value-container', 'children'),
        Input('batch-action', 'value')
    )
    def display_batch_value_input(action):
        """Show appropriate input for batch action"""
        from dash_app.layouts.components import create_tag_dropdown
        from dash import dcc
        
        if action == 'tag':
            return html.Div([
                create_tag_dropdown('batch-tag-dropdown', multi=True),
                dbc.Input(
                    id='batch-value',
                    type='text',
                    placeholder='Or enter custom tags (comma-separated)',
                    className='mb-2'
                )
            ])
        elif action == 'note':
            return dbc.Input(
                id='batch-value',
                type='text',
                placeholder='Note Value',
                className='mb-2'
            )
        return html.Div(id='batch-value', style={'display': 'none'})
    
    
    @app.callback(
        Output('selected-count', 'children'),
        Input('data-table', 'selected_rows'),
        State('data-table', 'data')
    )
    def show_selected_count(selected_rows, data):
        """Display count of selected rows"""
        if not selected_rows:
            return "No rows selected"
        return f"**{len(selected_rows)}** row(s) selected"
    
    
    @app.callback(
        Output('toast-container', 'children', allow_duplicate=True),
        Input('batch-execute', 'n_clicks'),
        State('batch-action', 'value'),
        State('batch-tag-dropdown', 'value'),
        State('batch-value', 'value'),
        State('data-table', 'selected_rows'),
        State('data-table', 'derived_virtual_data'),
        State('current-table', 'data'),
        prevent_initial_call=True
    )
    def execute_batch_operation(n_clicks, action, selected_tags, value,
                            selected_rows, derived_data, current_table):
        """Execute batch operations on selected rows"""
        if not n_clicks or not action or not selected_rows:
            return None
        
        if current_table != 'qc_data':
            return dbc.Toast(
                "Batch operations only available for QC data",
                header="Notice",
                is_open=True,
                duration=3000,
                className='bg-warning text-dark'
            )
        
        if not derived_data:
            return dbc.Toast(
                "No data available",
                header="Error",
                is_open=True,
                duration=3000,
                className='bg-danger text-white'
            )
        
        # FIX: Extract ID + wave from derived_data directly
        selected_subjects = []
        for idx in selected_rows:
            if idx < len(derived_data):
                row = derived_data[idx]
                selected_subjects.append((row['ID'], row['wave']))
        
        if action == 'tag':
            tags_to_add = []
            if selected_tags:
                tags_to_add.extend(selected_tags)
            if value:
                tags_to_add.extend([t.strip() for t in value.split(',') if t.strip()])
            
            if not tags_to_add:
                return dbc.Toast(
                    "Please enter at least one tag.",
                    header="Action Required",
                    is_open=True,
                    duration=4000,
                    className='bg-warning text-dark'
                )
            
            count = 0
            for sid, wave in selected_subjects:
                for tag in tags_to_add:
                    db.add_tag(sid, wave, tag, user='dash_user')
                count += 1
            
            message = f"Added {len(tags_to_add)} tag(s) to **{count}** subjects"
        
        elif action == 'note':
            if not value:
                return dbc.Toast(
                    "Please enter a note.",
                    header="Action Required",
                    is_open=True,
                    duration=4000,
                    className='bg-warning text-dark'
                )
            count = db.batch_update(selected_subjects, 'notes', value, user='dash_user')
            message = f"Added note to **{count}** subjects"
        else:
            message = "Invalid operation"
        
        return dbc.Toast(
            message,
            header="Batch Operation Complete",
            is_open=True,
            duration=4000,
            className='bg-primary text-white'
        )
    
    @app.callback(
        Output('toast-container', 'children', allow_duplicate=True),
        Input('delete-selected', 'n_clicks'),
        [State('data-table', 'selected_rows'),
         State('data-table', 'derived_virtual_data'),
         State('current-table', 'data')],
        prevent_initial_call=True
    )
    def delete_selected_rows(n_clicks, selected_rows, derived_data, current_table):
        """Delete selected rows - FIXED for pagination"""
        if not n_clicks or not selected_rows:
            return None
        
        if current_table != 'qc_data':
            return dbc.Toast(
                "Deletion only allowed for QC data",
                header="Notice",
                is_open=True,
                duration=3000,
                className='bg-warning text-dark'
            )
        
        if not derived_data:
            return dbc.Toast(
                "No data available",
                header="Error",
                is_open=True,
                duration=3000,
                className='bg-danger text-white'
            )
        
        subjects_to_delete = []
        for idx in selected_rows:
            if idx < len(derived_data):
                row = derived_data[idx]
                subjects_to_delete.append((row['ID'], row['wave']))
        
        deleted_count = 0
        for sid, wave in subjects_to_delete:
            db.delete_subject(sid, wave)
            deleted_count += 1
        
        return dbc.Toast(
            f"Successfully deleted **{deleted_count}** record(s).",
            header="Deletion Complete",
            is_open=True,
            duration=4000,
            className='bg-danger text-white'
        )
    
    
    @app.callback(
        Output('tables-list', 'children'),
        [Input('refresh-tables', 'n_clicks'),
         Input('import-table-modal', 'is_open')]
    )
    def display_tables_list(n_clicks, modal_state):
        """Display list of tables with delete buttons"""
        tables = db.get_all_tables()
        
        tables_items = []
        for table in tables:
            if table['table_name'] == 'qc_data':
                tables_items.append(
                    dbc.ListGroupItem([
                        html.Span(f"Primary: {table['display_name']}", className="me-auto"),
                        dbc.Badge("QC Data", color="success")
                    ], className="d-flex justify-content-between align-items-center")
                )
            else:
                tables_items.append(
                    dbc.ListGroupItem([
                        html.Span(table['display_name'], className="me-auto"),
                        dbc.Button(
                            "Delete",
                            id={'type': 'delete-table-btn', 'index': table['table_name']},
                            color="danger",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                )
        
        return dbc.ListGroup(tables_items)
    
    
    @app.callback(
        Output('toast-container', 'children', allow_duplicate=True),
        Input({'type': 'delete-table-btn', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def delete_secondary_table(n_clicks):
        """Delete a secondary table"""
        ctx = callback_context
        if not ctx.triggered or not any(n_clicks):
            return dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        table_name = json.loads(trigger_id)['index']
        
        try:
            db.delete_table(table_name)
            return dbc.Toast(
                f"Successfully deleted table '{table_name}'",
                header="Table Deleted",
                is_open=True,
                duration=3000,
                className='bg-success text-white'
            )
        except Exception as e:
            return dbc.Toast(
                f"Error deleting table: {str(e)}",
                header="Error",
                is_open=True,
                duration=4000,
                className='bg-danger text-white'
            )