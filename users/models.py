from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    def get_employees(self):
        return CustomUser.objects.filter(department=self, role=CustomUser.Role.EMPLOYEE)
    

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        CUSTOMER = 'CUSTOMER', 'Customer'
    
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_employees'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Ensure admins have correct permissions
        if self.role == self.Role.ADMIN and not self.is_superuser:
            self.is_staff = True
            self.is_superuser = True
        
        # Ensure username is unique
        if not self.pk:  # Only for new users
            base_username = self.username
            counter = 1
            while CustomUser.objects.filter(username=self.username).exists():
                self.username = f"{base_username}{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['last_name', 'first_name']
        permissions = [
            ("can_manage_users", "Can manage users"),
            ("can_manage_grievances", "Can manage grievances"),
        ]

# Signal to add permissions when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def set_user_permissions(sender, instance, created, **kwargs):
    if created:
        if instance.role == CustomUser.Role.ADMIN:
            admin_group, _ = Group.objects.get_or_create(name='Admins')
            instance.groups.add(admin_group)
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()
        elif instance.role == CustomUser.Role.EMPLOYEE:
            employee_group, _ = Group.objects.get_or_create(name='Employees')
            instance.groups.add(employee_group)