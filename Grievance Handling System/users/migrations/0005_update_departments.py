from django.db import migrations

def update_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    
    # Delete all existing departments
    Department.objects.all().delete()
    
    # Create new departments
    departments = [
        ("Customer Service", "Handles customer inquiries and support requests"),
        ("Technical Support", "Provides technical assistance and troubleshooting"),
        ("Development", "Software development and engineering team"),
        ("Quality Assurance", "Ensures product quality and testing"),
        ("Product Management", "Manages product strategy and roadmap")
    ]
    
    for name, description in departments:
        Department.objects.create(name=name, description=description)

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_alter_customuser_department'),
    ]

    operations = [
        migrations.RunPython(update_departments),
    ] 