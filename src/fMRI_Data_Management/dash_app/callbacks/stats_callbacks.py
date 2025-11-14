from dash import callback, Output, Input
import dash_bootstrap_components as dbc
from dash import html
from utils.plots import (
    create_radar_chart,
    create_stacked_bar_chart,
    create_waffle_chart,
    create_time_series_chart,
    get_summary_stats
)
from utils.data_processing import parse_qc_metrics
from config.constants import COLORS

def register_stats_callbacks(app, db):
    """Register statistics visualization callbacks"""
    
    @app.callback(
        [Output('stats-cards', 'children'),
         Output('radar-chart', 'figure'),
         Output('bar-chart', 'figure'),
         Output('waffle-chart', 'figure'),
         Output('time-series-chart', 'figure')],
        Input('filtered-data', 'data')
    )
    def update_statistics(filtered_data):
        """Update all statistics visualizations"""
        # Always use QC data for statistics
        qc_raw_data = db.get_all_data_raw()
        if not qc_raw_data:
            return [], {}, {}, {}, {}
        
        df = parse_qc_metrics(qc_raw_data)
        stats = get_summary_stats(df)
        
        # Create summary cards
        cards = [
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(stats['total']), className="card-title"),
                        html.P("Total Subjects", className="card-text")
                    ])
                ], style={"backgroundColor": COLORS['card'][0], "color": "white"})
            ], md=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(stats['wave1']), className="card-title"),
                        html.P("Wave 1", className="card-text")
                    ])
                ], style={"backgroundColor": COLORS['card'][1], "color": "white"})
            ], md=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(stats['wave2']), className="card-title"),
                        html.P("Wave 2", className="card-text")
                    ])
                ], style={"backgroundColor": COLORS['card'][2], "color": "white"})
            ], md=4)
        ]
        
        return (
            cards,
            create_radar_chart(df),
            create_stacked_bar_chart(df),
            create_waffle_chart(df),
            create_time_series_chart(df)
        )


