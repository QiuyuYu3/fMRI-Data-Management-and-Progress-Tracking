import sqlite3
from datetime import datetime, timedelta
import random

db_path = r'C:\Users\qy49547\Desktop\scripts\fMRI_Data_Management\fmri_qc.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT ID, wave, created_at FROM qc_data")
rows = cursor.fetchall()

for row in rows:
    subject_id, wave, old_created_at = row
    
    days_ago = random.randint(0, 180)
    created_date = datetime.now() - timedelta(days=days_ago)
    updated_date = created_date + timedelta(hours=random.randint(1, 48))
    
    new_created_at = created_date.strftime('%Y-%m-%d %H:%M')
    new_updated_at = updated_date.strftime('%Y-%m-%d %H:%M')
    
    cursor.execute("""
        UPDATE qc_data 
        SET created_at = ?, updated_at = ?
        WHERE ID = ? AND wave = ?
    """, (new_created_at, new_updated_at, subject_id, wave))

conn.commit()

cursor.execute("SELECT ID, wave, created_at, updated_at FROM qc_data LIMIT 5")

for row in cursor.fetchall():
    print(row)

conn.close()