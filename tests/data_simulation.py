import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NUM_SUBJECTS = 50
PROJECTS = ['BRANCH', 'ProjectA', 'ProjectB']
QC_VALUES = [0, 1, None]
REGRESS_VALUES = ['A', 'B', 'C', None]

def generate_qc_wave(wave_name):
    data = []
    for subject_id in range(1, NUM_SUBJECTS + 1):
        days_ago = random.randint(0, 180)
        created_date = datetime.now() - timedelta(days=days_ago)
        
        record = {
            'ID': str(subject_id).zfill(3),
            'wave': wave_name,
            'projects': random.choice(PROJECTS) if random.random() > 0.1 else None,
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
            'regress': random.choice(REGRESS_VALUES),
            'projectspace': random.choice(QC_VALUES),
            'PPG_correct': random.choice(QC_VALUES) if random.random() > 0.7 else None,
            'cglab': random.choice(QC_VALUES) if random.random() > 0.8 else None,
            'rescan': 1 if random.random() > 0.9 else 0,
            'notes': random.choice([None, 'Good quality', 'Motion artifacts', 'Needs review', '']),
            'tags': random.choice(['', 'needs re-run', 'incomplete RS', 'check quality']) if random.random() > 0.7 else '',
        }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_behavioral_wave(wave_name):
    data = []
    for subject_id in range(1, NUM_SUBJECTS + 1):
        if random.random() > 0.3:
            record = {
                'ID': str(subject_id).zfill(3),
                'wave': wave_name,
                'projects': random.choice(PROJECTS),
                'test_date': (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d'),
                'iq_score': random.randint(85, 130) if random.random() > 0.1 else None,
                'memory_score': round(random.uniform(0, 100), 1) if random.random() > 0.15 else None,
                'attention_score': round(random.uniform(0, 100), 1) if random.random() > 0.15 else None,
                'completion_status': random.choice(['complete', 'partial', 'incomplete', None]),
                'notes': random.choice([None, 'Normal', 'Below average', 'Excellent'])
            }
            data.append(record)
    return pd.DataFrame(data)

if __name__ == '__main__':
    qc_wave1 = generate_qc_wave('wave1')
    qc_wave2 = generate_qc_wave('wave2')
    qc_wave1.to_csv('qc_wave1.csv', index=False)
    qc_wave2.to_csv('qc_wave2.csv', index=False)
    print(f"Generated {len(qc_wave1)} wave1 QC records -> qc_wave1.csv")
    print(f"Generated {len(qc_wave2)} wave2 QC records -> qc_wave2.csv")
    
    beh_wave1 = generate_behavioral_wave('wave1')
    beh_wave2 = generate_behavioral_wave('wave2')
    beh_wave1.to_csv('behavioral_wave1.csv', index=False)
    beh_wave2.to_csv('behavioral_wave2.csv', index=False)
    print(f"Generated {len(beh_wave1)} wave1 behavioral records -> behavioral_wave1.csv")
    print(f"Generated {len(beh_wave2)} wave2 behavioral records -> behavioral_wave2.csv")