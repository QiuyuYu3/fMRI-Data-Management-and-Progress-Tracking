# Color Schemes
COLORS = {
    'primary': '#264e70',
    'success': '#679186',
    'danger': '#f9b4ab',
    'info': '#bbd4ce',
    'warning': '#fdebd3',
    'secondary': '#9AA5B1',
    
    # Chart colors
    'chart': ['#264e70', '#fdebd3', '#f9b4ab', '#679186', '#bbd4ce'],
    'card': ['#264e70', '#679186', '#f9b4ab'],
}

# QC Status Colors
QC_STATUS_COLORS = {
    0: '#D3D3D3',
    1: '#FFD93D',
    2: '#FF6B6B',
    3: '#6BCF7F'
}

# Predefined Tags
PREDEFINED_TAGS = [
    'needs re-run',
    'incomplete RS',
    'incomplete kidvid',
    'incomplete CARDS',
    'incomplete T1',
    'duplicate runs T1',
    'duplicate runs RS',
    'duplicate runs kidvid',
    'duplicate runs CARDS',
    'good_quality',
    'needs_review',
    'scanner_issue',
    'rescan_required',
    'artifacts',
    'motion',
    'mislabeled',
    'exclude'
]

# Metric Groups for Charts
METRIC_GROUPS = {
    'structural': ['T1', 'kidvid', 'CARDS', 'RS'],
    'qc': ['kidvid_QC', 'Cards_QC', 'RS_QC'],
    'all': ['reconstruction', 'T1', 'kidvid', 'kidvid_QC', 
            'CARDS', 'Cards_QC', 'RS', 'RS_QC', 'Download', 'PPG']
}
 
# Projects and Waves
PROJECTS = ['BRANCH', 'DORRY']

# WAVES = ['wave1', 'wave2']

QC_OPTIONS = [
    {'label': 'Done (1)', 'value': 1},
    {'label': 'TODO (0)', 'value': 0}
]

#TODO: Remove this function after implementing dynamic note templates
# Default Note Templates
DEFAULT_NOTE_TEMPLATES = [
    ("Motion artifacts", "Motion artifacts detected", "qc"),
    ("Good quality", "Good quality scan", "qc"),
    ("Incomplete scan", "Incomplete scan - subject moved", "scanner"),
    ("Scanner issue", "Scanner malfunction", "scanner"),
    ("Needs rescan", "Needs rescan", "rescan"),
    ("Under review", "Under review by QC team", "qc"),
]

# Database Configuration
DB_CONFIG = {
    'default_path': 'fmri_qc.db',
    'check_same_thread': False
}

# Table Configuration
TABLE_CONFIG = {
    'non_editable_columns': ['ID', 'wave', 'created_at', 'updated_at', 
                            'view_details', 'row_id', 'notes'],
    'metadata_columns': ['created_at', 'updated_at', 'updated_by'],
    'fixed_qc_fields': ['PPG', 'PPG_correct', 'cglab', 'projects', 
                        'Download', 'rescan', 'notes', 'tags']
}

# Page Size Options
PAGE_SIZE_OPTIONS = [10, 25, 50, 100]
DEFAULT_PAGE_SIZE = 25

# Quick Filter Buttons
# need to change callbacks
QUICK_FILTERS = {
    'rescan': {'label': 'Show Rescan', 'color': 'info'},
    # 'incomplete': {'label': 'Show Incomplete QC', 'color': 'warning'},
    'notes': {'label': 'Show With Notes', 'color': 'info'},
    'week': {'label': 'Show This Week', 'color': 'secondary'},
    'need_rerun': {'label': 'Need Re-run', 'color': 'danger'},
    # 'needs_review': {'label': 'Needs Review', 'color': 'warning'}
}

# Batch Operation Types
#TODO: add user name option
BATCH_OPERATIONS = [
    {'label': 'Add tag', 'value': 'tag'},
    {'label': 'Add note', 'value': 'note'}
]

DEFAULT_HIDDEN_COLUMNS = [
    'created_at', 
    'updated_at',
    'PPG_correct'
]