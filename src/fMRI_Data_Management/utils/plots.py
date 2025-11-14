import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

def create_stacked_bar_chart(df):
    metrics_group1 = ['T1', 'kidvid', 'CARDS', 'RS']
    metrics_group2 = ['kidvid_QC', 'Cards_QC', 'RS_QC']

    if 'wave' not in df.columns:
        df['wave'] = 'all'
    waves = sorted(df['wave'].unique())

    colors = ["#7BAFD4","#C9D7E8","#E8D9C5","#F2C9C1","#B6CEC7","#A3C4BC",
              "#D7E3F4","#F5D8CC","#E3E0DA","#C8D9D4"]

    metric_groups = [metrics_group1, metrics_group2]
    all_metrics = metrics_group1 + metrics_group2
    color_map = {m: colors[idx % len(colors)] for idx, m in enumerate(all_metrics)}

    n_rows = len(metric_groups)

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,  # space between subplots
        subplot_titles=["Structural Metrics", "QC Metrics"]
    )

    def get_counts(metrics):
        data = []
        for wave in waves:
            wave_df = df[df['wave'] == wave]
            counts = [wave_df[m].notna().sum() if m in wave_df.columns else 0 for m in metrics]
            data.append(counts)
        return pd.DataFrame(data, index=waves, columns=metrics)

    counts_list = [get_counts(g) for g in metric_groups]

    # Add stacked bars for each group
    for row_idx, (counts, metrics) in enumerate(zip(counts_list, metric_groups), start=1):
        for i, metric in enumerate(metrics):
            fig.add_trace(
                go.Bar(
                    y=counts.index,
                    x=counts[metric],
                    name=metric,
                    orientation='h',
                    marker_color=color_map[metric],
                    hovertemplate=f"{metric}: %{{x}}<extra></extra>"
                ),
                row=row_idx, col=1
            )

    fig.update_layout(
        barmode='stack',
        title="QC Metrics Count by Wave",
        height=400,
        showlegend=True,
        paper_bgcolor='white',
        plot_bgcolor='rgba(245,245,245,0.5)',
        font=dict(size=11),
        hovermode='x unified',
        # xaxis_title="Count",
        # yaxis_title="Wave",
        title_y=0.95,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor='rgba(220,220,220,0.4)')
    fig.update_yaxes(showgrid=False)

    return fig


def create_radar_chart(df):
    """Create faceted radar chart for QC metrics count by wave"""
    
    def hex_to_rgb(hex_color):
        """Converts a hex color string (#rrggbb) to an RGB tuple (r, g, b)."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    metrics = ['reconstruction', 'T1', 'kidvid', 'kidvid_QC', 'CARDS', 'Cards_QC', 'RS', 'RS_QC', 'Download', 'PPG']
    
    if 'wave' not in df.columns:
        df['wave'] = 'all'
    
    waves = sorted(df['wave'].unique())
    n_waves = len(waves)
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=n_waves,
        specs=[[{'type': 'polar'}] * n_waves],
        subplot_titles=[f"{w.title()}" for w in waves]
    )

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for idx, wave in enumerate(waves, 1):
        wave_df = df[df['wave'] == wave]
        
        # Count non-null values for each metric
        counts = []
        for metric in metrics:
            if metric in wave_df.columns:
                counts.append(wave_df[metric].notna().sum())
            else:
                counts.append(0)
        
        color = colors[idx % len(colors)]
        
        # Convert hex to RGB before creating the rgba fillcolor string
        r, g, b = hex_to_rgb(color)
        fill_color_rgba = f'rgba({r}, {g}, {b}, 0.3)'
        
        fig.add_trace(
            go.Scatterpolar(
                r=counts,
                theta=metrics,
                fill='toself',
                name=wave.title(),
                line=dict(color=color, width=2),
                fillcolor=fill_color_rgba,
                showlegend=False,
                hovertemplate='%{theta}: %{r}<extra></extra>'
            ),
            row=1, col=idx
        )
        
        fig.update_polars(
            radialaxis=dict(
                visible=True,
                range=[0, max(counts) * 1.2] if counts and max(counts) > 0 else [0, 1],
                showline=True,
                linewidth=1,
                gridcolor='rgba(150, 150, 150, 0.5)'
            ),
            angularaxis=dict(
                linewidth=1,
                showline=True,
                gridcolor='rgba(150, 150, 150, 0.5)'
            ),
            bgcolor='rgba(0, 0, 0, 0)',
            row=1, col=idx,
            domain=dict(y=[0.1, 0.9])
        )
    
    fig.update_layout(
        title="QC Metrics Coverage by Wave",
        height=500,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        font=dict(size=11),
        hoverlabel=dict(
            bgcolor='rgba(50, 50, 50, 0.9)',
            font_size=12,
            font_family="Arial",
            font_color='white'
        )
    )
    for i, annotation in enumerate(fig['layout']['annotations']):
        annotation['y'] = 1.0
    return fig


def create_waffle_chart(df):
    """
    Create square heatmap visualization (waffle-style) with IDs as rows, metrics as columns.
    Wave1 and Wave2 side by side.
    """
    metrics = ['reconstruction', 'T1', 'kidvid', 'kidvid_QC', 'CARDS', 'Cards_QC', 'RS', 'RS_QC', 'Download', 'PPG']
    
    # Filter only available metrics
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=14, color='gray')
        )
        return fig

    status_colors = {
        0: '#D3D3D3',
        1: '#F8786E',
        2: '#FFD966',
        3: '#C5E0B3'
    }
    
    if 'wave' not in df.columns:
        df = df.copy()
        df['wave'] = 'all'
    
    waves = sorted(df['wave'].unique())
    n_waves = len(waves)
    
    fig = make_subplots(
        rows=1, cols=n_waves,
        subplot_titles=[f"{wave.title()}" for wave in waves],
        horizontal_spacing=0.05
    )
    
    # Target cell size in pixels
    cell_size = 15
    max_ids = 0
    
    for idx, wave in enumerate(waves, start=1):
        wave_df = df[df['wave'] == wave].sort_values('ID')
        
        if wave_df.empty:
            continue
        
        # Create matrix data (IDs as rows, metrics as columns)
        matrix_data = []
        hover_texts = []
        
        for _, subject in wave_df.iterrows():
            row_values = []
            row_hover = []
            
            for metric in available_metrics:
                val = subject.get(metric)
                if pd.isna(val):
                    row_values.append(0)
                    status_text = 'NA'
                elif val == 1:
                    row_values.append(3)
                    status_text = 'Done'
                elif val == 0:
                    row_values.append(1)
                    status_text = 'TODO'
                else:
                    row_values.append(2)
                    status_text = f'Other ({val})'
                
                row_hover.append(f"Wave: {wave}<br>ID: {subject['ID']}<br>Metric: {metric}<br>Status: {status_text}")
            
            matrix_data.append(row_values)
            hover_texts.append(row_hover)
        
        n_ids = len(wave_df)
        max_ids = max(max_ids, n_ids)
        
        ids = wave_df['ID'].tolist()
        
        colorscale = [
            [0.0, status_colors[0]],
            [0.33, status_colors[1]],
            [0.66, status_colors[2]],
            [1.0, status_colors[3]]
        ]
        
        fig.add_trace(
            go.Heatmap(
                z=matrix_data,
                x=available_metrics,
                y=ids,
                colorscale=colorscale,
                showscale=False,
                xgap=2,
                ygap=2,
                hoverinfo='text',
                hovertext=hover_texts,
                zmin=0,
                zmax=3,
            ),
            row=1, col=idx
        )
        
        # Update axes for this subplot
        fig.update_xaxes(
            tickangle=45,
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='lightgray',
            side='bottom',
            row=1, col=idx
        )
        
        fig.update_yaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='lightgray',
            row=1, col=idx
        )
    
    # Calculate figure dimensions for square cells
    n_metrics = len(available_metrics)
    fig_width = (cell_size * n_metrics + 150) * n_waves + 100
    fig_height = cell_size * max_ids + 200
    
    # Add custom legend using dummy traces
    legend_items = [
        ('Done (1)', status_colors[3]),
        ('TODO (0)', status_colors[1]),
        ('NA', status_colors[0]),
        ('Other', status_colors[2])
    ]
    
    for label, color in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color=color, symbol='square'),
            showlegend=True,
            name=label
        ))
    
    fig.update_layout(
        title="Status Matrix by Wave",
        height=fig_height,
        width=fig_width,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            title=dict(text="Status")
        ),
        margin=dict(l=100, r=50, t=80, b=80),
        hoverlabel=dict(
            bgcolor='rgba(50, 50, 50, 0.9)',
            font_size=12,
            font_family="Arial",
            font_color='white'
        )
    )
    
    return fig


# def create_time_series_chart(df):
#     """Create time series chart showing weekly subject entry count with area fill"""
#     if 'created_at' not in df.columns or df.empty:
#         fig = go.Figure()
#         fig.add_annotation(
#             text="No timestamp data available",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, 
#             showarrow=False,
#             font=dict(size=14, color='gray')
#         )
#         return fig
    
#     try:
#         # Convert to datetime with flexible format
#         df = df.copy()
#         df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce')
        
#         # Remove rows with invalid dates
#         df = df.dropna(subset=['created_at'])
        
#         if df.empty:
#             raise ValueError("No valid dates found")
        
#         # Group by week
#         df['week'] = df['created_at'].dt.to_period('W').dt.start_time
        
#         weekly_counts = df.groupby('week').size().reset_index(name='count')
        
#         # Fill missing weeks with 0
#         if not weekly_counts.empty:
#             date_range = pd.date_range(
#                 start=weekly_counts['week'].min(),
#                 end=weekly_counts['week'].max(),
#                 freq='W-MON'
#             )
#             full_range = pd.DataFrame({'week': date_range})
#             weekly_counts = full_range.merge(weekly_counts, on='week', how='left').fillna(0)
        
#         fig = go.Figure()
        
#         # Custom colors for time series (Deep Blue/Teal line with light fill)
#         line_color = '#1f77b4' # Deep Blue
#         fill_color = 'rgba(31, 119, 180, 0.3)'
#         peak_color = '#d62728' # Bright Red for peaks
        
#         # Add area fill
#         fig.add_trace(go.Scatter(
#             x=weekly_counts['week'],
#             y=weekly_counts['count'],
#             mode='lines',
#             name='Subjects per Week',
#             line=dict(color=line_color, width=1.5),
#             fill='tozeroy',
#             fillcolor=fill_color,
#             hovertemplate='Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>'
#         ))
        
#         # Add markers on peaks
#         if len(weekly_counts) > 0:
#             max_count = weekly_counts['count'].max()
#             if max_count > 0:
#                 peak_weeks = weekly_counts[weekly_counts['count'] == max_count]
#                 fig.add_trace(go.Scatter(
#                     x=peak_weeks['week'],
#                     y=peak_weeks['count'],
#                     mode='markers',
#                     marker=dict(
#                         size=12,
#                         color=peak_color, # Bright Red for peaks
#                         symbol='star',
#                         line=dict(width=2, color='white')
#                     ),
#                     name='Peak Week',
#                     hovertemplate='Peak: %{y} subjects<extra></extra>'
#                 ))
        
#         fig.update_layout(
#             title="Subject Entry Timeline (Weekly)",
#             xaxis_title="Week",
#             yaxis_title="Number of Subjects",
#             hovermode='x unified', # Set hover mode to 'x unified' for better data review
#             height=400,
#             xaxis=dict(
#                 showgrid=True,
#                 gridcolor='rgba(200, 200, 200, 0.3)',
#                 showline=True,
#                 linewidth=1,
#                 linecolor='lightgray',
#                 zeroline=False
#             ),
#             yaxis=dict(
#                 showgrid=True,
#                 gridcolor='rgba(200, 200, 200, 0.3)',
#                 showline=True,
#                 linewidth=1,
#                 linecolor='lightgray',
#                 zeroline=True,
#                 zerolinewidth=1,
#                 zerolinecolor='lightgray'
#             ),
#             paper_bgcolor='white',
#             plot_bgcolor='rgba(245, 245, 250, 0.5)',
#             font=dict(size=11),
#             legend=dict(
#                 orientation="h",
#                 yanchor="bottom",
#                 y=1.02,
#                 xanchor="right",
#                 x=1
#             )
#         )
        
#         return fig
        
#     except Exception as e:
#         fig = go.Figure()
#         fig.add_annotation(
#             text=f"Error processing dates: {str(e)}",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5, 
#             showarrow=False,
#             font=dict(size=14, color='red')
#         )
#         return fig




def create_time_series_chart(df):
    if 'created_at' not in df.columns or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No timestamp data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='gray')
        )
        return fig

    try:
        df = df.copy()
        df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce')
        df = df.dropna(subset=['created_at'])
        if df.empty:
            raise ValueError("No valid dates found")

        if 'wave' not in df.columns:
            df['wave'] = 'all'

        df['week'] = df['created_at'].dt.to_period('W').dt.start_time
        weekly_counts = df.groupby(['week', 'wave']).size().reset_index(name='count')

        date_range = pd.date_range(
            start=weekly_counts['week'].min(),
            end=weekly_counts['week'].max(),
            freq='W-MON'
        )
        waves = sorted(df['wave'].unique())
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']
        peak_color = '#d62728'

        fig = go.Figure()
        global_max = 0
        global_peak_week = None

        for i, wave in enumerate(waves):
            wave_df = weekly_counts[weekly_counts['wave'] == wave]
            full_range = pd.DataFrame({'week': date_range})
            wave_df = full_range.merge(wave_df, on='week', how='left').fillna({'count': 0, 'wave': wave})

            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=wave_df['week'],
                y=wave_df['count'],
                mode='lines',
                name=str(wave).title(),
                line=dict(color=color, width=1.5),
                fill='tozeroy',
                fillcolor=f'rgba({int(color[1:3],16)},'
                          f'{int(color[3:5],16)},'
                          f'{int(color[5:7],16)},0.2)',
                hovertemplate='Wave: %{text}<br>Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>',
                text=[wave] * len(wave_df)
            ))

            wave_max = wave_df['count'].max()
            if wave_max > global_max:
                global_max = wave_max
                global_peak_week = wave_df.loc[wave_df['count'] == wave_max, 'week'].iloc[0]

        if global_max > 0 and global_peak_week is not None:
            fig.add_trace(go.Scatter(
                x=[global_peak_week],
                y=[global_max],
                mode='markers',
                marker=dict(size=14, color=peak_color, symbol='star', line=dict(width=2, color='white')),
                name='Global Peak',
                hovertemplate='Global Peak<br>Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>'
            ))

        fig.update_layout(
            title="Subject Entry Timeline by Wave (Weekly)",
            xaxis_title="Week",
            yaxis_title="Number of Subjects",
            hovermode='x unified',
            height=400,
            xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.3)',
                       showline=True, linewidth=1, linecolor='lightgray', zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.3)',
                       showline=True, linewidth=1, linecolor='lightgray',
                       zeroline=True, zerolinewidth=1, zerolinecolor='lightgray'),
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,245,250,0.5)',
            font=dict(size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error processing dates: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='red')
        )
        return fig


def get_summary_stats(df):
    """Calculate summary statistics for cards"""
    total = len(df)
    wave1 = len(df[df['wave'] == 'wave1']) if 'wave' in df.columns else 0
    wave2 = len(df[df['wave'] == 'wave2']) if 'wave' in df.columns else 0
    
    # Calculate completion rate
    completed = 0
    if 'notes' in df.columns:
        completed = len(df[df['notes'].notna() & (df['notes'] != '')])
    
    return {
        'total': total,
        'wave1': wave1,
        'wave2': wave2,
        'completed': completed
    }