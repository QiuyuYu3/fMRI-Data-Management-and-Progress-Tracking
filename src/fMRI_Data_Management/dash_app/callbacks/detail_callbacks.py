from dash import callback, Output, Input, State, callback_context, dash, dash_table
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from utils.data_processing import parse_qc_metrics
from config.constants import TABLE_CONFIG

def register_detail_callbacks(app, db):
    """Register subject detail modal callbacks"""
    
    @app.callback(
        [Output('subject-detail-modal', 'is_open'),
        Output('detail-modal-title', 'children'),
        Output('subject-summary-card', 'children'),
        Output('detail-tab-content', 'children'),
        Output('detail-subject-context', 'data')],
        [Input('data-table', 'active_cell'),
        Input('close-detail', 'n_clicks'),
        Input('detail-tabs', 'active_tab')],
        [State('data-table', 'data'),
        State('data-table', 'derived_virtual_data'),
        State('data-table', 'page_current'),
        State('data-table', 'page_size'),
        State('subject-detail-modal', 'is_open'),
        State('current-table', 'data'),
        State('detail-subject-context', 'data')],
        prevent_initial_call=True
    )
    def manage_detail_modal(active_cell, close_clicks, active_tab,
                        table_data, derived_data,
                        page_current, page_size,
                        is_open, current_table, subject_context):
        ctx = callback_context
        if not ctx.triggered:
            return False, "", "", "", None
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'close-detail':
            return False, "", "", "", None
        
        # Tab switch - regenerate content with saved context
        if trigger_id == 'detail-tabs' and is_open and subject_context:
            subject_id = subject_context.get('subject_id')
            all_data = db.get_subject_all_tables_data(subject_id)
            tab_content = create_tab_content(active_tab, all_data, current_table, db)
            return True, dash.no_update, dash.no_update, tab_content, subject_context
        
        # Click on view_details
        if trigger_id == 'data-table' and active_cell:
            if active_cell.get('column_id') != 'view_details':
                return False, "", "", "", None
            
            row_index = active_cell['row']
            page_current = page_current or 0
            page_size = page_size or 25
            global_row_index = page_current * page_size + row_index

            if not derived_data or global_row_index >= len(derived_data):
                return False, "", "", "", None

            clicked_row = derived_data[global_row_index]
            subject_id = clicked_row.get('ID')
            wave = clicked_row.get('wave', '')
            
            if not subject_id:
                return False, "", "", "", None
            
            # Save context
            subject_context = {
                'subject_id': str(subject_id),
                'wave': str(wave)
            }
            
            all_data = db.get_subject_all_tables_data(str(subject_id))
            title = f"Subject Details: {subject_id} - {wave}"
            row_id = clicked_row.get('row_id', None)
            if row_id:
                title += f" (Row: {row_id})"
            
            qc_data = all_data.get('qc_data', [])
            summary_card = create_summary_card(subject_id, qc_data, all_data)
            
            if not active_tab:
                active_tab = 'tab-waves'
            
            tab_content = create_tab_content(active_tab, all_data, current_table, db)
            
            return True, title, summary_card, tab_content, subject_context
        
        return False, "", "", "", None

def create_summary_card(subject_id, qc_data, all_data):
    """Create summary card for subject"""
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"Subject: {subject_id}", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.P([html.Strong("Total Scans: "), str(len(qc_data))]),
                    html.P([html.Strong("Tables with Data: "), 
                           str(sum(1 for v in all_data.values() if v))])
                ], md=6),
                dbc.Col([
                    html.P([html.Strong("Rescans: "), 
                           str(sum(1 for d in qc_data if d.get('rescan') == 1))]),
                    html.P([html.Strong("Latest Update: "), 
                           qc_data[0].get('updated_at', 'N/A')[:10] if qc_data else 'N/A'])
                ], md=6)
            ])
        ])
    ], className='bg-light')


def create_tab_content(active_tab, all_data, current_table, db):
    """Create content for different tabs"""
    
    if active_tab == 'tab-all-tables':
        tables_content = []
        for table_name, data in all_data.items():
            if data:
                table_info = db.get_table_info(table_name)
                df = pd.DataFrame(data)
                if table_name == 'qc_data':
                    df = parse_qc_metrics(data)
                
                tables_content.append(html.Div([
                    html.H6(f"{table_info['display_name']}", className="mt-3 mb-2"),
                    dash_table.DataTable(
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'fontSize': '12px'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                    )
                ]))
        
        return html.Div(tables_content) if tables_content else html.P("No data", className="text-muted")
    
    elif active_tab == 'tab-timeline':
        timeline_items = []
        for table_name, data in all_data.items():
            for record in data:
                if 'created_at' in record:
                    timeline_items.append({
                        'date': record['created_at'],
                        'table': db.get_table_info(table_name)['display_name'],
                        'wave': record.get('wave', 'N/A')
                    })
        
        timeline_items.sort(key=lambda x: x['date'], reverse=True)
        
        timeline_content = [
            html.Div([
                dbc.Badge(item['date'][:10], color="secondary", className="me-2"),
                html.Span(f"{item['table']} - {item['wave']}", className="ms-2")
            ], className="mb-2")
            for item in timeline_items[:20]
        ]
        
        return html.Div(timeline_content) if timeline_content else html.P("No timeline data", className="text-muted")
    
    else:
        if current_table and all_data.get(current_table):
            df = pd.DataFrame(all_data[current_table])
            if current_table == 'qc_data':
                df = parse_qc_metrics(all_data[current_table])
            
            comparison_table = dash_table.DataTable(
                columns=[{"name": i, "id": i, 
                         'editable': i not in TABLE_CONFIG['non_editable_columns']} 
                        for i in df.columns],
                data=df.to_dict('records'),
                editable=True,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'minWidth': '100px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
            
            table_info = db.get_table_info(current_table)
            return html.Div([
                html.H5(f"Wave Comparison - {table_info['display_name']}", className="mb-3"),
                comparison_table
            ])
        else:
            return html.P("No data available", className="text-muted")