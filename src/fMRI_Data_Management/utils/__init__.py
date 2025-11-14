from utils.data_processing import (
    parse_qc_metrics,
    extract_tags_from_string,
    tags_to_json,
    get_all_unique_tags,
    filter_dataframe_by_criteria,
    apply_quick_filter,
    prepare_export_dataframe
)

from utils.file_operations import (
    decode_uploaded_file,
    prepare_temp_csv,
    cleanup_temp_file,
    export_dataframe_to_csv,
    read_csv_safe
)

from utils.validators import (
    validate_subject_input,
    validate_table_name,
    validate_csv_structure
)

# Import plots if available
try:
    from utils.plots import (
        create_stacked_bar_chart,
        create_radar_chart,
        create_waffle_chart,
        create_time_series_chart,
        get_summary_stats
    )
    __all_plots__ = [
        'create_stacked_bar_chart',
        'create_radar_chart',
        'create_waffle_chart',
        'create_time_series_chart',
        'get_summary_stats'
    ]
except ImportError:
    print("[WARNING] utils.plots not found. Visualization functions unavailable.")
    __all_plots__ = []

__all__ = [
    # Data processing
    'parse_qc_metrics',
    'extract_tags_from_string',
    'tags_to_json',
    'get_all_unique_tags',
    'filter_dataframe_by_criteria',
    'apply_quick_filter',
    'prepare_export_dataframe',
    
    # File operations
    'decode_uploaded_file',
    'prepare_temp_csv',
    'cleanup_temp_file',
    'export_dataframe_to_csv',
    'read_csv_safe',
    
    # Validators
    'validate_subject_input',
    'validate_table_name',
    'validate_csv_structure',
] + __all_plots__
