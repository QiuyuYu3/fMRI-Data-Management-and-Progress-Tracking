from dash_app.app import create_app
from database import FMRIQCDatabase, init_default_templates

# Import all callback registration functions
from dash_app.callbacks.import_callbacks import register_import_callbacks
from dash_app.callbacks.filter_callbacks import register_filter_callbacks
from dash_app.callbacks.data_callbacks import register_data_callbacks
from dash_app.callbacks.modal_callbacks import register_modal_callbacks
from dash_app.callbacks.tag_callbacks import register_tag_callbacks
from dash_app.callbacks.detail_callbacks import register_detail_callbacks
from dash_app.callbacks.stats_callbacks import register_stats_callbacks
from dash_app.callbacks.export_callbacks import register_export_callbacks
from dash_app.callbacks.notes_callbacks import register_notes_callbacks

db = FMRIQCDatabase("fmri_qc.db")
init_default_templates(db)

app = create_app(db)

# Register all callbacks
register_filter_callbacks(app, db)
register_data_callbacks(app, db)
register_modal_callbacks(app, db)
register_tag_callbacks(app, db)
register_detail_callbacks(app, db)
register_stats_callbacks(app, db)
register_export_callbacks(app, db)
register_import_callbacks(app, db)
register_notes_callbacks(app, db)
if __name__ == '__main__':
    app.run(debug=True, port=8050)