# grievances/management/commands/reset_grievance_ids.py
import os
import sqlite3
from django.core.management.base import BaseCommand
from django.db import transaction
from grievances.models import Grievance, GrievanceLog

class Command(BaseCommand):
    help = 'Resets grievance IDs to sequential numbers'

    def handle(self, *args, **options):
        db_path = os.path.join('db.sqlite3')
        
        # Create backup first
        self.create_backup(db_path)
        
        with transaction.atomic():
            try:
                # Get all grievances in order
                grievances = list(Grievance.objects.all().order_by('created_at'))
                
                # Disable foreign key constraints temporarily
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=OFF")
                    conn.commit()
                
                # Update IDs sequentially
                for index, grievance in enumerate(grievances, start=1):
                    if grievance.id != index:
                        # Update related logs first
                        GrievanceLog.objects.filter(grievance_id=grievance.id).update(grievance_id=index)
                        # Then update the grievance
                        Grievance.objects.filter(id=grievance.id).update(id=index)
                
                # Reset sequence counter
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE sqlite_sequence SET seq = ? WHERE name = ?",
                        (len(grievances), 'grievances_grievance')
                    )
                    cursor.execute("PRAGMA foreign_keys=ON")
                    conn.commit()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully reset {len(grievances)} grievance IDs'
                ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error resetting IDs: {str(e)}'
                ))
                raise

    def create_backup(self, db_path):
        backup_path = db_path + '.bak'
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(db_path, backup_path)
        os.rename(backup_path, db_path)  # Keep original but we have backup
        self.stdout.write(self.style.WARNING(
            'Created database backup at db.sqlite3.bak'
        ))