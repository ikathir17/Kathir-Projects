import sqlite3
import os
from django.conf import settings

def reset_grievance_ids():
    # 1. Configure database path
    db_path = settings.DATABASES['default']['NAME']
    
    # 2. Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting ID reset process...")
        
        # 3. Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # 4. Get current grievances in creation order
        cursor.execute("SELECT id FROM grievances_grievance ORDER BY created_at")
        grievances = cursor.fetchall()
        
        # 5. Create ID mapping (old → new)
        id_map = {old_id: new_id for new_id, (old_id,) in enumerate(grievances, start=1)}
        print(f"ID mapping created for {len(id_map)} grievances")
        
        # 6. Update related GrievanceLog entries
        updated_logs = 0
        for old_id, new_id in id_map.items():
            if old_id != new_id:
                cursor.execute(
                    "UPDATE grievances_grievancelog SET grievance_id=? WHERE grievance_id=?",
                    (new_id, old_id)
                )
                updated_logs += cursor.rowcount
        print(f"Updated {updated_logs} log entries")
        
        # 7. Update grievance IDs
        updated_grievances = 0
        for old_id, new_id in id_map.items():
            if old_id != new_id:
                cursor.execute(
                    "UPDATE grievances_grievance SET id=? WHERE id=?",
                    (new_id, old_id)
                )
                updated_grievances += cursor.rowcount
        print(f"Updated {updated_grievances} grievance IDs")
        
        # 8. Reset SQLite sequence counter
        cursor.execute(
            "UPDATE sqlite_sequence SET seq=? WHERE name=?",
            (len(id_map), 'grievances_grievance')
        )
        
        conn.commit()
        print("✔ Successfully reset grievance IDs")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        # 9. Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        conn.close()

if __name__ == "__main__":
    # 10. Configure Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grievance_system.settings")
    import django
    django.setup()
    
    # 11. Create backup first
    import shutil
    shutil.copy2('db.sqlite3', 'db.sqlite3.bak')
    print("Created backup at db.sqlite3.bak")
    
    # 12. Run the reset
    reset_grievance_ids()