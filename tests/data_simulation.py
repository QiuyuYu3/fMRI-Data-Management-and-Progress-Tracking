import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
NUM_SUBJECTS = 50
WAVES = ['1', '2', '3']
PROJECTS = ['BRANCH', 'ProjectA', 'ProjectB']

# QC metric options
QC_VALUES = [0, 1, None]
REGRESS_VALUES = ['A', 'B', 'C', None]

def generate_qc_data():
    """Generate mock QC data"""
    data = []
    
    for subject_id in range(1, NUM_SUBJECTS + 1):
        for wave in random.sample(WAVES, k=random.randint(1, 3)):  # Random waves
            
            # Base date for this record
            days_ago = random.randint(0, 180)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            record = {
                'ID': str(subject_id).zfill(3),  # 001, 002, etc.
                'wave': wave,
                'projects': random.choice(PROJECTS) if random.random() > 0.1 else None,
                
                # QC metrics (some missing)
                'reconstruction': random.choice(QC_VALUES),
                'T1': random.choice(QC_VALUES),
                'kidvid': random.choice(QC_VALUES),
                'kidvid_QC': random.choice(QC_VALUES),
                'CARDS': random.choice(QC_VALUES),
                'Cards_QC': random.choice(QC_VALUES),
                'RS': random.choice(QC_VALUES),
                'RS_QC': random.choice(QC_VALUES),
                'Download': random.choice(QC_VALUES),
                'PPG': random.choice(QC_VALUES),
                
                # Other fields
                'regress': random.choice(REGRESS_VALUES),
                'projectspace': random.choice(QC_VALUES),
                'PPG_correct': random.choice(QC_VALUES) if random.random() > 0.7 else None,
                'cglab': random.choice(QC_VALUES) if random.random() > 0.8 else None,
                
                # Rescan flag
                'rescan': 1 if random.random() > 0.9 else 0,
                
                # Notes (some have, some don't)
                'notes': random.choice([
                    None,
                    'Good quality scan',
                    'Motion artifacts detected',
                    'Needs review',
                    'Participant fell asleep',
                    ''
                ]),
                
                # Tags (as comma-separated string for CSV)
                'tags': random.choice([
                    '',
                    'needs re-run',
                    'incomplete RS',
                    'needs re-run,incomplete kidvid',
                    'check quality'
                ]) if random.random() > 0.7 else '',
                
                # Timestamps
                'created_at': created_date.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': (created_date + timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S'),
                'updated_by': random.choice(['user1', 'user2', 'dash_user'])
            }
            
            data.append(record)
    
    return pd.DataFrame(data)

def generate_behavioral_data():
    """Generate mock behavioral test data (extra table example)"""
    data = []
    
    for subject_id in range(1, NUM_SUBJECTS + 1):
        if random.random() > 0.3:  # Not all subjects have behavioral data
            for wave in random.sample(WAVES, k=random.randint(1, 2)):
                record = {
                    'ID': str(subject_id).zfill(3),
                    'wave': wave,
                    'projects': random.choice(PROJECTS),
                    'test_date': (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d'),
                    'iq_score': random.randint(85, 130) if random.random() > 0.1 else None,
                    'memory_score': round(random.uniform(0, 100), 1) if random.random() > 0.15 else None,
                    'attention_score': round(random.uniform(0, 100), 1) if random.random() > 0.15 else None,
                    'completion_status': random.choice(['complete', 'partial', 'incomplete', None]),
                    'notes': random.choice([None, 'Normal performance', 'Below average', 'Excellent'])
                }
                data.append(record)
    
    return pd.DataFrame(data)

# Generate and save data
if __name__ == '__main__':
    # Generate QC data
    qc_df = generate_qc_data()
    qc_df.to_csv('mock_qc_data.csv', index=False)
    print(f"Columns: {list(qc_df.columns)}")
    print(qc_df.head(3))
    
    # Generate behavioral data
    behavioral_df = generate_behavioral_data()
    behavioral_df.to_csv('mock_behavioral_data.csv', index=False)
    print(f"Columns: {list(behavioral_df.columns)}")
    print(behavioral_df.head(3))