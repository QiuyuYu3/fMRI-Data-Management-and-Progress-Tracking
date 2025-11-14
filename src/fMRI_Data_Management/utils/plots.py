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

def create_time_series_chart(df):
    """Create combined time series: overall trend + by-wave breakdown"""
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
        
        # Overall weekly counts
        overall_counts = df.groupby('week').size().reset_index(name='count')
        
        # By-wave weekly counts
        wave_counts = df.groupby(['week', 'wave']).size().reset_index(name='count')
        
        # Get date range for filling gaps
        date_range = pd.date_range(
            start=df['week'].min(),
            end=df['week'].max(),
            freq='W-MON'
        )
        full_range = pd.DataFrame({'week': date_range})
        
        # Fill missing weeks for overall
        overall_counts = full_range.merge(overall_counts, on='week', how='left').fillna(0)
        
        # Get sorted wave values
        waves = sorted([w for w in df['wave'].unique() if w != 'all'])
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#d62728']
        
        # Create 2x1 subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Overall Subject Entry Timeline", "Subject Entry by Wave"),
            vertical_spacing=0.12,
            row_heights=[0.4, 0.6]
        )
        
        # Top subplot: Overall trend
        overall_color = '#1f77b4'
        fig.add_trace(
            go.Scatter(
                x=overall_counts['week'],
                y=overall_counts['count'],
                mode='lines',
                name='All Waves',
                line=dict(color=overall_color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba(31, 119, 180, 0.2)',
                hovertemplate='Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add peak marker for overall
        if len(overall_counts) > 0 and overall_counts['count'].max() > 0:
            max_count = overall_counts['count'].max()
            peak_week = overall_counts.loc[overall_counts['count'] == max_count, 'week'].iloc[0]
            fig.add_trace(
                go.Scatter(
                    x=[peak_week],
                    y=[max_count],
                    mode='markers',
                    marker=dict(size=12, color='#d62728', symbol='star', 
                               line=dict(width=2, color='white')),
                    name='Peak',
                    hovertemplate='Peak<br>Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>',
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Bottom subplot: By wave
        global_max = 0
        global_peak_week = None
        
        for i, wave in enumerate(waves):
            wave_df = wave_counts[wave_counts['wave'] == wave]
            wave_df = full_range.merge(wave_df, on='week', how='left').fillna({'count': 0, 'wave': wave})
            
            color = colors[i % len(colors)]
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            
            # Convert wave value to display format
            wave_label = f"Wave {wave}" if wave != 'all' else 'All'
            
            fig.add_trace(
                go.Scatter(
                    x=wave_df['week'],
                    y=wave_df['count'],
                    mode='lines',
                    name=wave_label,
                    line=dict(color=color, width=1.5),
                    fill='tozeroy',
                    fillcolor=f'rgba({r}, {g}, {b}, 0.2)',
                    hovertemplate=f'{wave_label}<br>Week: %{{x|%Y-%m-%d}}<br>Subjects: %{{y}}<extra></extra>',
                    legendgroup=wave_label
                ),
                row=2, col=1
            )
            
            # Track global peak
            wave_max = wave_df['count'].max()
            if wave_max > global_max:
                global_max = wave_max
                global_peak_week = wave_df.loc[wave_df['count'] == wave_max, 'week'].iloc[0]
        
        # Add global peak marker for by-wave plot
        if global_max > 0 and global_peak_week is not None:
            fig.add_trace(
                go.Scatter(
                    x=[global_peak_week],
                    y=[global_max],
                    mode='markers',
                    marker=dict(size=12, color='#d62728', symbol='star',
                               line=dict(width=2, color='white')),
                    name='Peak',
                    hovertemplate='Peak<br>Week: %{x|%Y-%m-%d}<br>Subjects: %{y}<extra></extra>',
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_xaxes(
            showgrid=True, gridcolor='rgba(200,200,200,0.3)',
            showline=True, linewidth=1, linecolor='lightgray',
            zeroline=False,
            row=1, col=1
        )
        fig.update_xaxes(
            showgrid=True, gridcolor='rgba(200,200,200,0.3)',
            showline=True, linewidth=1, linecolor='lightgray',
            zeroline=False,
            title_text="Week",
            row=2, col=1
        )
        
        fig.update_yaxes(
            showgrid=True, gridcolor='rgba(200,200,200,0.3)',
            showline=True, linewidth=1, linecolor='lightgray',
            zeroline=True, zerolinewidth=1, zerolinecolor='lightgray',
            title_text="Number of Subjects",
            row=1, col=1
        )
        fig.update_yaxes(
            showgrid=True, gridcolor='rgba(200,200,200,0.3)',
            showline=True, linewidth=1, linecolor='lightgray',
            zeroline=True, zerolinewidth=1, zerolinecolor='lightgray',
            title_text="Number of Subjects",
            row=2, col=1
        )
        
        fig.update_layout(
            height=700,
            hovermode='x unified',
            paper_bgcolor='white',
            plot_bgcolor='rgba(245,245,250,0.5)',
            font=dict(size=11),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            showlegend=True
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
    """Calculate summary statistics - handles dynamic wave values"""
    total = len(df)
    
    # Dynamic wave counting
    wave_stats = {}
    if 'wave' in df.columns:
        waves = sorted([w for w in df['wave'].unique() if pd.notna(w)])
        for wave in waves:
            wave_stats[f'wave_{wave}'] = len(df[df['wave'] == wave])
    
    # Completion rate
    completed = 0
    if 'notes' in df.columns:
        completed = len(df[df['notes'].notna() & (df['notes'] != '')])
    
    result = {
        'total': total,
        'completed': completed,
        'waves': wave_stats
    }
    return result