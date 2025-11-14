from dash_app.callbacks.data_callbacks import register_data_callbacks
from dash_app.callbacks.filter_callbacks import register_filter_callbacks
from dash_app.callbacks.import_callbacks import register_import_callbacks
from dash_app.callbacks.stats_callbacks import register_stats_callbacks
from dash_app.callbacks.export_callbacks import register_export_callbacks
from dash_app.callbacks.tag_callbacks import register_tag_callbacks
from dash_app.callbacks.detail_callbacks import register_detail_callbacks
from dash_app.callbacks.modal_callbacks import register_modal_callbacks


def register_all_callbacks(app, database):
    print("[INFO] Registering callbacks...")
    
    register_data_callbacks(app, database)
    
    register_filter_callbacks(app, database)
    
    register_import_callbacks(app, database)
    
    register_stats_callbacks(app, database)
    
    register_export_callbacks(app, database)
    
    register_tag_callbacks(app, database)
    
    register_detail_callbacks(app, database)

    register_modal_callbacks(app, database)



__all__ = [
    'register_all_callbacks',
    'register_data_callbacks',
    'register_filter_callbacks',
    'register_import_callbacks',
    'register_stats_callbacks',
    'register_export_callbacks',
    'register_tag_callbacks',
    'register_detail_callbacks',
    'register_modal_callbacks'
]


