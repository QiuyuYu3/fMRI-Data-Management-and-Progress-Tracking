import dash
import dash_bootstrap_components as dbc
from dash_app.layouts.main_layout import create_main_layout
from config.constants import COLORS

def create_app(database):
    CUSTOM_CSS = f"""
    /* Custom Button Styles */
    .btn-custom-primary {{
        background-color: {COLORS['primary']} !important;
        border-color: {COLORS['primary']} !important;
        color: white !important;
    }}
    .btn-custom-success {{
        background-color: {COLORS['success']} !important;
        border-color: {COLORS['success']} !important;
        color: white !important;
    }}
    .btn-custom-danger {{
        background-color: {COLORS['danger']} !important;
        border-color: {COLORS['danger']} !important;
        color: black !important;
    }}
    .btn-custom-info {{
        background-color: {COLORS['info']} !important;
        border-color: {COLORS['info']} !important;
        color: black !important;
    }}
    .btn-custom-warning {{
        background-color: {COLORS['warning']} !important;
        border-color: {COLORS['warning']} !important;
        color: black !important;
    }}
    .btn-custom-secondary {{
        background-color: {COLORS['secondary']} !important;
        border-color: {COLORS['secondary']} !important;
        color: white !important;
    }}

    /* Custom Card Backgrounds */
    .card-op-add {{
        background-color: {COLORS['primary']} !important;
        color: white;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .card-op-delete {{
        background-color: {COLORS['danger']} !important;
        color: white !important;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .card-op-export {{
        background-color: {COLORS['success']} !important;
        color: white;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .card-op-export-selected {{
        background-color: {COLORS['info']} !important;
        color: black;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .card-op-import {{
        background-color: {COLORS['warning']} !important;
        color: black;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .card-op-warning:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }}
    .card-op-add:hover, .card-op-delete:hover, .card-op-export:hover,
    .card-op-export-selected:hover, .card-op-import:hover {{
        transform: scale(1.05);
    }}
    """
    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {'{%metas%}'}
            <title>{'{%title%}'}</title>
            {'{%favicon%}'}
            {'{%css%}'}
            <style>{CUSTOM_CSS}</style>
        </head>
        <body>
            {'{%app_entry%}'}
            <footer>
                {'{%config%}'}
                {'{%scripts%}'}
                {'{%renderer%}'}
            </footer>
        </body>
    </html>
    '''
    
    app.title = "fMRI Progress Tracking Dashboard"
    app.config.suppress_callback_exceptions = True
    
    app.db = database

    app.layout = create_main_layout()
    
    return app



