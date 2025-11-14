import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash_app.layouts.modals import (
    create_add_subject_modal,
    create_import_csv_modal,
    create_import_table_modal,
    create_tag_editor_modal,
    create_subject_detail_modal,
    create_notes_editor_modal
)
from dash_app.layouts.components import (
    create_page_size_selector,
    create_quick_filter_buttons
)
from config.constants import COLORS, PREDEFINED_TAGS, BATCH_OPERATIONS, PAGE_SIZE_OPTIONS

def create_main_layout():
    return dbc.Container([
        html.H1("fMRI Progress Tracking Dashboard", className='mt-4 mb-4'),
        
        dbc.Row([
            # Left Sidebar
            dbc.Col([
                create_batch_section(),
                create_column_selector(),
                create_filter_section(),
                create_manage_tables_section(),
            ], width=3, style={
                "backgroundColor": "#f8f9fa", 
                "padding": "20px", 
                "borderRight": "1px solid #dee2e6", 
                "overflowY": "auto"
            }),
            
            # Main Content Area
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab([
                        create_operation_cards(),
                        create_table_selector(),
                        create_table_section()
                    ], label="Data Management"),
                    dbc.Tab([create_stats_section()], label="Statistics"),
                ])
            ], width=9)
        ]),
        
        # Modals
        create_add_subject_modal(),
        create_import_csv_modal(),
        create_import_table_modal(),
        create_tag_editor_modal(),
        create_subject_detail_modal(),
        create_notes_editor_modal(),
        
        # Data stores
        dcc.Store(id='filtered-data'),
        dcc.Store(id='uploaded-csv-data'),
        dcc.Store(id='uploaded-table-csv-data'),
        dcc.Store(id='tag-edit-context'),
        dcc.Store(id='current-table', data='qc_data'),
        dcc.Store(id='detail-subject-context'), 
        dcc.Store(id='notes-edit-context'),
        
        # Download component
        dcc.Download(id='download-csv'),
        
        # Toast container
        html.Div(id='toast-container', style={
            'position': 'fixed', 
            'top': 20, 
            'right': 20, 
            'zIndex': 9999
        })
    ], fluid=True)


def create_batch_section():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Batch Operations", className="mb-3"),
            html.Div(id='selected-count', className='mb-2'),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Action"),
                    dcc.Dropdown(
                        id='batch-action',
                        options=BATCH_OPERATIONS,
                        placeholder='Select action',
                        className='mb-2'
                    )
                ], md=12),
                dbc.Col(html.Div(id='batch-value-container'), md=12),
                dbc.Col([
                    dbc.Button(
                        "Execute",
                        id='batch-execute',
                        className='btn-custom-primary w-100 mt-2'
                    )
                ], md=12)
            ], className="g-2")
        ])
    ], className='mb-3')


def create_filter_section():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="mb-3"),
            html.P("(Filters apply to Main data only)", className="text-muted small"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Search ID"),
                    dbc.Input(id='filter-id', type='text', placeholder='e.g., 0011')
                ], width=12),
                dbc.Col([
                    dbc.Label("Wave"),
                    dcc.Dropdown(id='filter-wave', placeholder='All waves', clearable=True)
                ], width=12),
                dbc.Col([
                    dbc.Label("Rescan"),
                    dcc.Dropdown(
                        id='filter-rescan',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': 'Rescan', 'value': '1'},
                            {'label': 'No rescan', 'value': '0'}
                        ],
                        value='all'
                    )
                ], width=12),
                dbc.Col([
                    dbc.Label("Tags"),
                    dcc.Dropdown(id='filter-tags', placeholder='All tags', clearable=True)
                ], width=12),
                dbc.Col([
                    dbc.Label("Notes contain"),
                    dbc.Input(id='filter-notes', type='text', placeholder='Search notes')
                ], width=12),
            ], className="g-2"),
            html.Hr(),
            dbc.Row([
                dbc.Col(create_quick_filter_buttons())
            ])
        ])
    ], className='mb-3')


def create_column_selector():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Column Visibility", className="mb-3"),
            dcc.Dropdown(
                id='column-selector',
                options=[],
                value=[],
                multi=True,
                placeholder='Select columns to hide'
            )
        ])
    ], className='mb-3')


def create_manage_tables_section():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Manage Tables", className="mb-3"),
            html.Div(id='tables-list'),
            dbc.Button(
                "Refresh",
                id='refresh-tables',
                className='btn-custom-secondary btn-sm mt-2'
            )
        ])
    ], className='mb-3')


def create_operation_cards():
    return dbc.Row([
        dbc.Col(
            dbc.Button(
                html.H5("Add New Subject", className="card-title text-center my-1"),
                id='add-new-row',
                n_clicks=0,
                className='card-op-add shadow-sm w-100',
                style={'padding': '1rem', 'height': '100%', 'border': 'none'}
            ),
            md=2, className='mb-2'
        ),
        
        dbc.Col(
            dbc.Button(
                html.H5("Import Tracking Table", className="card-title text-center my-1"),
                id='import-csv-btn',
                n_clicks=0,
                className='card-op-import shadow-sm w-100',
                style={'padding': '1rem', 'height': '100%', 'border': 'none'}
            ),
            md=2, className='mb-2'
        ),
        
        dbc.Col(
            dbc.Button(
                html.H5("Import Extra Table", className="card-title text-center my-1"),
                id='import-table-btn',
                n_clicks=0,
                className='card-op-warning shadow-sm w-100',
                style={
                    'padding': '1rem',
                    'height': '100%',
                    'border': 'none',
                    'backgroundColor': "#e4d8ed",  # Changed to info color
                    'color': 'black',
                    'transition': 'transform 0.2s, box-shadow 0.2s',  # Added animation
                    'cursor': 'pointer'
                }
            ),
            md=2, className='mb-2'
        ),
        
        dbc.Col(
            dbc.Button(
                html.H5("Export All Data", className="card-title text-center my-1"),
                id='export-all',
                n_clicks=0,
                className='card-op-export shadow-sm w-100',
                style={'padding': '1rem', 'height': '100%', 'border': 'none'}
            ),
            md=2, className='mb-2'
        ),
        
        dbc.Col(
            dbc.Button(
                html.H5("Export Selected", className="card-title text-center my-1"),
                id='export-selected',
                n_clicks=0,
                className='card-op-export-selected shadow-sm w-100',
                style={'padding': '1rem', 'height': '100%', 'border': 'none'}
            ),
            md=2, className='mb-2'
        ),

        dbc.Col(
            dbc.Button(
                html.H5("Delete Selected", className="card-title text-center my-1"),
                id='delete-selected',
                n_clicks=0,
                className='card-op-delete shadow-sm w-100',
                style={'padding': '1rem', 'height': '100%', 'border': 'none'}
            ),
            md=2, className='mb-2'
        ),
    ], className="mb-3 g-3", style={'marginTop': '20px'})


def create_table_selector():
    return dbc.Row([
        dbc.Col([
            html.Label("View Table:", className="me-2 fw-bold"),
            dcc.Dropdown(
                id='table-selector',
                options=[],
                value='qc_data',
                clearable=False,
                style={'minWidth': '250px'}
            )
        ], width="auto", className="d-flex align-items-center")
    ], className="mb-3")


def create_table_section():
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H5(id='table-title', className="mb-0"), width="auto"),
                dbc.Col(create_page_size_selector(), width="auto"),
            ], className="mb-3 g-0 justify-content-between align-items-center"),
            
            dash_table.DataTable(
                id='data-table',
                columns=[],
                data=[],
                editable=True,
                filter_action='native',
                sort_action='native',
                row_selectable='multi',
                selected_rows=[],
                page_action='native',
                page_current=0,
                page_size=25,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'minWidth': '100px'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'filter_query': '{rescan} = 1'}, 'backgroundColor': "#eef3e0"},
                    {'if': {'filter_query': '{tags} contains "needs re-run"'}, 'backgroundColor': '#fdecea'},
                    {'if': {'column_id': 'notes'}, 'whiteSpace': 'normal', 'height': 'auto'},
                    {'if': {'column_id': 'view_details'}, 'textAlign': 'center'}
                ]
            )
        ])
    ])


def create_stats_section():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Statistics Overview", className="mb-3"),
            # html.P("Statistics based on Main data only", className="text-muted small"),
            dbc.Row(id='stats-cards', className='mb-3'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='radar-chart')], md=12)
            ], className='mt-3'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='bar-chart')], md=12)
            ], className='mt-3'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='time-series-chart')], md=12)
            ], className='mt-3'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='waffle-chart')], md=12)
            ], className='mt-3')
        ])
    ], className='mb-3')



