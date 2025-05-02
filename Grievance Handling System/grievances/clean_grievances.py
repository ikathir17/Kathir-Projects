# grievances/clean_grievances.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grievance_system.settings')
django.setup()

from django.db import connection
from grievances.models import Grievance, GrievanceLog, GrievanceUpdate, Attachment

def clear_all_grievance_data():
    # Disable foreign key checks (MySQL/PostgreSQL specific)
    with connection.cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
    
    # Delete all data without triggering signals or model methods
    Grievance.objects.all().delete()
    GrievanceLog.objects.all().delete()
    GrievanceUpdate.objects.all().delete()
    Attachment.objects.all().delete()
    
    with connection.cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
    
    print("All grievance data has been cleared successfully.")

if __name__ == '__main__':
    clear_all_grievance_data()