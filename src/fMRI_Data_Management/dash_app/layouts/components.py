import dash_bootstrap_components as dbc
from dash import dcc, html
from config.constants import (
    PREDEFINED_TAGS, 
    PROJECTS, 
    # WAVES, 
    QC_OPTIONS,
    QUICK_FILTERS, 
    BATCH_OPERATIONS, 
    PAGE_SIZE_OPTIONS,
    DEFAULT_PAGE_SIZE
)

def create_project_dropdown(dropdown_id: str, required: bool = False, md: int = 4):
    label_text = "Project *" if required else "Project"
    return dbc.Col([
        dbc.Label(label_text), 
        dcc.Dropdown(
            id=dropdown_id, 
            options=[{'label': p, 'value': p} for p in PROJECTS],
            value='BRANCH' if required else None,
            placeholder='Select project',
            clearable=not required
        )
    ], md=md)


def create_wave_dropdown(dropdown_id: str, required: bool = False, md: int = 4):
    """Create a wave dropdown that will be populated dynamically"""
    label_text = "Wave *" if required else "Wave"
    return dbc.Col([
        dbc.Label(label_text), 
        dcc.Dropdown(
            id=dropdown_id, 
            options=[],  # Start with empty options, will be populated by callback
            placeholder='Select wave',
            clearable=not required
        )
    ], md=md)


def create_qc_metric_dropdown(dropdown_id: str, label: str, md: int = 4):
    return dbc.Col([
        dbc.Label(label), 
        dcc.Dropdown(
            id=dropdown_id, 
            options=QC_OPTIONS,
            placeholder='Optional',
            clearable=True
        )
    ], md=md)


def create_tag_dropdown(dropdown_id: str, multi: bool = False):
    return dcc.Dropdown(
        id=dropdown_id,
        options=[{'label': tag, 'value': tag} for tag in PREDEFINED_TAGS],
        placeholder='Select tags' + (' (multiple)' if multi else ''),
        multi=multi,
        className='mb-2'
    )


def create_quick_filter_buttons():
    """Create quick filter button group"""
    buttons = []
    for key, config in QUICK_FILTERS.items():
        buttons.append(
            dbc.Button(
                config['label'], 
                id=f'quick-{key}', 
                className=f'btn-custom-{config["color"]} me-2 mt-1', 
                size='sm'
            )
        )
    return buttons


def create_page_size_selector(dropdown_id: str = 'page-size-dropdown'):
    return html.Div([
        dbc.Label("Rows per page:", className="me-2 mb-0"),
        dcc.Dropdown(
            id=dropdown_id, 
            options=[{'label': str(i), 'value': i} for i in PAGE_SIZE_OPTIONS], 
            value=DEFAULT_PAGE_SIZE, 
            clearable=False, 
            style={'width': '100px'}
        )
    ], className='d-flex align-items-center')


def create_filter_input(input_id: str, label: str, placeholder: str = ""):
    return dbc.Col([
        dbc.Label(label),
        dbc.Input(id=input_id, type='text', placeholder=placeholder)
    ], width=12)


def create_filter_dropdown(dropdown_id: str, label: str, 
                          options: list = None, placeholder: str = ""):
    return dbc.Col([
        dbc.Label(label),
        dcc.Dropdown(
            id=dropdown_id, 
            options=options or [], 
            placeholder=placeholder, 
            clearable=True
        )
    ], width=12)


def create_user_input(input_id: str = 'import-user', default_value: str = 'dash_user'):
    return dbc.Col([
        dbc.Label("User"),
        dbc.Input(id=input_id, placeholder='Your name', value=default_value)
    ], md=4)


def create_upload_button(upload_id: str, button_text: str = "Select CSV File"):
    return dcc.Upload(
        id=upload_id,
        children=dbc.Button(button_text, className='btn-custom-primary'),
        multiple=False
    )


def create_info_alert(message: str, color: str = "info"):
    return dbc.Alert(message, color=color, className="mb-3")


