import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_app.layouts.components import (
    create_project_dropdown,
    create_wave_dropdown,
    create_qc_metric_dropdown,
    create_tag_dropdown
)

def create_add_subject_modal():
    return dbc.Modal([
        dbc.ModalHeader("Add New Subject"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Subject ID *"),
                    dbc.Input(id='new-subject-id', type='text', placeholder='e.g., 0001')
                ], md=3),
                create_wave_dropdown('new-subject-wave', required=True),
                create_project_dropdown('new-subject-project', required=True),
                dbc.Col([
                    dbc.Label("Reconstruction"),
                    dcc.Dropdown(
                        id='new-reconstruction',
                        options=[
                            {'label': 'Done (1)', 'value': 1},
                            {'label': 'TODO (0)', 'value': 0}
                        ],
                        placeholder='Optional'
                    )
                ], md=3)
            ], className='mb-3'),
            
            dbc.Row([
                create_qc_metric_dropdown('new-t1', 'T1'),
                create_qc_metric_dropdown('new-kidvid', 'kidvid'),
                create_qc_metric_dropdown('new-k-qc', 'k_QC'),
            ], className='mb-3'),
            
            dbc.Row([
                create_qc_metric_dropdown('new-cards', 'CARDS'),
                create_qc_metric_dropdown('new-c-qc', 'C_QC'),
                create_qc_metric_dropdown('new-rs', 'RS'),
            ], className='mb-3'),
            
            dbc.Row([
                create_qc_metric_dropdown('new-r-qc', 'R_QC'),
                create_qc_metric_dropdown('new-download', 'Download'),
                create_qc_metric_dropdown('new-ppg', 'PPG'),
            ], className='mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Notes"),
                    dbc.Textarea(id='new-notes', placeholder='Optional notes', rows=3)
                ], md=12)
            ], className='mb-3'),
            
            html.Div(id='add-subject-status')
        ]),
        
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-add-subject", className='btn-custom-secondary me-2'),
            dbc.Button("Add Subject", id="confirm-add-subject", className='btn-custom-primary')
        ])
    ], id='add-subject-modal', size='xl')


def create_import_csv_modal():
    """Create modal for importing CSV to QC data"""
    return dbc.Modal([
        dbc.ModalHeader("Import CSV to QC Data"),
        dbc.ModalBody([
            dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "CSV must contain 'ID' and 'wave' columns. Wave values will be auto-detected."
            ], color="info", className="mb-3"),
            
            dcc.Upload(
                id='upload-csv',
                children=dbc.Button("Select CSV File", className='btn-custom-primary'),
                multiple=False
            ),
            html.Hr(),
            dbc.Row([
                create_project_dropdown('import-project', required=True, md=6),
                dbc.Col([
                    dbc.Label("User"),
                    dbc.Input(id='import-user', placeholder='Your name', value='dash_user')
                ], md=6)
            ]),
            html.Hr(),
            html.Div(id='import-preview'),
            html.Div(id='import-status')
        ]),
        
        dbc.ModalFooter([
            dbc.Button("Close", id="close-import", className='btn-custom-secondary me-2'),
            dbc.Button("Import", id="confirm-import", className='btn-custom-primary', disabled=True)
        ])
    ], id='import-modal', size='xl')


def create_import_table_modal():
    """Create modal for importing additional tables"""
    return dbc.Modal([
        dbc.ModalHeader("Import Additional Table"),
        dbc.ModalBody([
            dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "CSV must contain 'ID' and 'wave' columns. Wave values will be auto-detected.",
                html.Br(),
                "Automatic row_id will be created as primary key.",
                html.Br(),
                "Allows duplicate ID+wave combinations for multiple runs."
            ], color="info", className="mb-3"),
            
            dcc.Upload(
                id='upload-table-csv',
                children=dbc.Button("Select CSV File", className='btn-custom-primary'),
                multiple=False
            ),
            
            html.Hr(),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Table Name *"),
                    dbc.Input(
                        id='table-name-input',
                        type='text',
                        placeholder='e.g., behavioral_data'
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("Display Name"),
                    dbc.Input(
                        id='table-display-name',
                        type='text',
                        placeholder='e.g., Behavioral Tests'
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("User"),
                    dbc.Input(
                        id='table-import-user',
                        type='text',
                        placeholder='Your name',
                        value='dash_user'
                    )
                ], md=4),
            ], className='mb-3'),
            
            dbc.Row([
                create_project_dropdown('table-import-project', required=True, md=6),
                dbc.Col([
                    dbc.Label("Description (optional)"),
                    dbc.Textarea(
                        id='table-description',
                        placeholder='Describe this table...',
                        rows=2
                    )
                ], md=6)
            ], className='mb-3'),
            
            html.Hr(),
            html.Div(id='table-import-preview'),
            html.Div(id='table-import-status')
        ]),
        
        dbc.ModalFooter([
            dbc.Button("Close", id="close-table-import", className='btn-custom-secondary me-2'),
            dbc.Button("Import Table", id="confirm-table-import", className='btn-custom-primary', disabled=True)
        ])
    ], id='import-table-modal', size='xl')

def create_tag_editor_modal():
    return dbc.Modal([
        dbc.ModalHeader("Edit Tags"),
        dbc.ModalBody([
            html.Div([
                dbc.Label("Current Tags:"),
                html.Div(id='current-tags-display', className='mb-3'),
                dbc.Label("Add Tag:"),
                create_tag_dropdown('tag-dropdown', multi=False),
                dbc.Input(
                    id='custom-tag-input',
                    type='text',
                    placeholder='Or enter custom tag',
                    className='mb-2'
                ),
                dbc.Button("Add Tag", id='add-tag-btn', className='btn-custom-primary mb-3'),
            ]),
            html.Div(id='tag-edit-status')
        ]),
        
        dbc.ModalFooter([
            dbc.Button("Close", id="close-tag-editor", className='btn-custom-secondary')
        ])
    ], id='tag-editor-modal', size='lg')


def create_subject_detail_modal():
    return dbc.Modal([
        dbc.ModalHeader(html.H4(id='detail-modal-title')),
        dbc.ModalBody([
            html.Div(id='subject-summary-card', className='mb-3'),
            
            dbc.Tabs([
                dbc.Tab(label="Wave Comparison", tab_id="tab-waves"),
                dbc.Tab(label="All Tables", tab_id="tab-all-tables"),
                dbc.Tab(label="Timeline & History", tab_id="tab-timeline"),
            ], id='detail-tabs', active_tab='tab-waves'),
            
            html.Div(id='detail-tab-content', className='mt-3')
        ]),
        
        dbc.ModalFooter([
            dbc.Button("Close", id="close-detail", className='btn-custom-secondary')
        ])
    ], id='subject-detail-modal', size='xl', scrollable=True)

def create_notes_editor_modal():
    return dbc.Modal([
        dbc.ModalHeader("Edit Notes"),
        dbc.ModalBody([
            dbc.Textarea(
                id='notes-editor-textarea',
                placeholder='Enter notes here...',
                rows=10,
                style={'width': '100%'}
            ),
            html.Div(id='notes-edit-status', className='mt-2')
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-notes-edit", className='btn-custom-secondary me-2'),
            dbc.Button("Save", id="save-notes-edit", className='btn-custom-primary')
        ])
    ], id='notes-editor-modal', size='lg')
