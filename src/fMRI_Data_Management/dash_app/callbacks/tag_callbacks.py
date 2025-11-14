from dash import callback, Output, Input, State, callback_context, ALL, dash
import dash_bootstrap_components as dbc
from dash import html
import json
from utils.data_processing import parse_qc_metrics

# row index/id could be tricky

def register_tag_callbacks(app, db):
    """Register tag editor callbacks"""
    
    @app.callback(
        [Output('tag-editor-modal', 'is_open'),
        Output('current-tags-display', 'children'),
        Output('tag-edit-context', 'data'),
        Output('toast-container', 'children', allow_duplicate=True),
        Output('data-table', 'data', allow_duplicate=True)],
        [Input('data-table', 'active_cell'),
        Input('close-tag-editor', 'n_clicks'),
        Input('add-tag-btn', 'n_clicks'),
        Input({'type': 'delete-tag-btn', 'index': ALL}, 'n_clicks')],
        [State('tag-edit-context', 'data'),
        State('tag-dropdown', 'value'),
        State('custom-tag-input', 'value'),
        State('data-table', 'derived_virtual_data'),
        State('data-table', 'page_current'),
        State('data-table', 'page_size'),
        State('data-table', 'data'),
        State('current-table', 'data')],
        prevent_initial_call=True
    )
    def manage_tag_editor(active_cell, close_clicks, add_clicks, delete_clicks,
                        context, selected_tag, custom_tag, derived_data, 
                        page_current, page_size, current_data, current_table):
        from utils.data_processing import parse_qc_metrics
        import pandas as pd
        
        ctx = callback_context
        if not ctx.triggered:
            return False, "", None, None, dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'close-tag-editor':
            return False, "", None, None, dash.no_update

        if trigger_id == 'data-table' and active_cell:
            if active_cell.get('column_id') == 'tags':
                row_index = active_cell['row']
                page_current = page_current or 0
                page_size = page_size or 25
                
                actual_index = page_current * page_size + row_index
                
                if not derived_data or actual_index >= len(derived_data):
                    return False, "", None, None, dash.no_update
                
                row_data = derived_data[actual_index]
                subject_id = str(row_data.get('ID'))
                wave = str(row_data.get('wave', ''))
                
                context = {'subject_id': subject_id, 'wave': wave}
                tags_list = db.get_subject_tags(subject_id, wave)
                tags_display = create_tags_display(tags_list)
                return True, tags_display, context, None, dash.no_update

        def refresh_table():
            if current_table == 'qc_data':
                raw_data = db.get_all_data_raw()
                df = parse_qc_metrics(raw_data)
            else:
                raw_data = db.get_table_data(current_table)
                df = pd.DataFrame(raw_data)
                if 'tags' in df.columns:
                    df['tags'] = df['tags'].apply(
                        lambda x: ', '.join(json.loads(x)) if x and x != 'null' else ''
                    )
            
            df['view_details'] = '🔍'
            
            # Keep same columns as current display
            if current_data and len(current_data) > 0:
                existing_cols = list(current_data[0].keys())
                available_cols = [col for col in existing_cols if col in df.columns]
                return df[available_cols].to_dict('records')
            
            return df.to_dict('records')

        if trigger_id == 'add-tag-btn' and context:
            tag_to_add = custom_tag or selected_tag
            if tag_to_add:
                db.add_tag(context['subject_id'], context['wave'], tag_to_add, user='dash_user')
                tags_list = db.get_subject_tags(context['subject_id'], context['wave'])
                
                refreshed_data = refresh_table()
                tags_display = create_tags_display(tags_list)
                toast = dbc.Toast(
                    f"Added '{tag_to_add}' to ID {context['subject_id']} ({context['wave']})",
                    header="Tag Added",
                    is_open=True, duration=3000, className='bg-success text-white'
                )
                return True, tags_display, context, toast, refreshed_data

        if 'delete-tag-btn' in trigger_id and context:
            trigger_data = json.loads(trigger_id)
            tag_to_delete = trigger_data['index']
            
            db.remove_tag(context['subject_id'], context['wave'], tag_to_delete, user='dash_user')
            tags_list = db.get_subject_tags(context['subject_id'], context['wave'])
            
            refreshed_data = refresh_table()
            tags_display = create_tags_display(tags_list)
            toast = dbc.Toast(
                f"Removed '{tag_to_delete}' from ID {context['subject_id']} ({context['wave']})",
                header="Tag Deleted",
                is_open=True, duration=3000, className='bg-info text-white'
            )
            return True, tags_display, context, toast, refreshed_data

        return False, dash.no_update, context, None, dash.no_update


def create_tags_display(tags_list):
    """Helper: Create tags display with delete buttons"""
    if not tags_list:
        return html.P("No tags", className="text-muted")
    
    return html.Div([
        dbc.Badge(
            [
                tag,
                html.Span(
                    " ×",
                    id={'type': 'delete-tag-btn', 'index': tag},
                    style={'marginLeft': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'}
                )
            ],
            color="primary",
            className="me-1 mb-1",
            style={'cursor': 'pointer'}
        )
        for tag in tags_list
    ])


