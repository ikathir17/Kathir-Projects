from django.db import migrations

def create_default_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    Department.objects.create(name="Technical", description="Technical support department")
    Department.objects.create(name="Billing", description="Billing and payments department")
    Department.objects.create(name="Customer Service", description="General customer support")

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # Replace with your last migration number
    ]

    operations = [
        migrations.RunPython(create_default_departments),
    ]