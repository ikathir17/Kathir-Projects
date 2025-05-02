from django.db import models
from users.models import CustomUser, Department
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
User = get_user_model()

class GrievanceLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('ASSIGNMENT', 'Assignment Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    grievance = models.ForeignKey('Grievance', on_delete=models.SET_NULL, null=True, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField()
    previous_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Grievance Audit Log"
        verbose_name_plural = "Grievance Audit Logs"



class Grievance(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'
        ESCALATED = 'ESCALATED', 'Escalated'
    
    class IssueType(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Technical Issues'
        CUSTOMER_SERVICE = 'CUSTOMER_SERVICE', 'Customer Service Issues'
        SOFTWARE_BUG = 'SOFTWARE_BUG', 'Software/Application Bugs'
        PRODUCT = 'PRODUCT', 'Product/Feature Issues'
        QUALITY = 'QUALITY', 'Quality Assurance Failures'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='grievances')
    issue_type = models.CharField(max_length=50, choices=IssueType.choices)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.RECEIVED)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_grievances')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        changes = {}
        
        if not is_new:
            try:
                # Track changes for existing grievances
                old = Grievance.objects.get(pk=self.pk)
                for field in ['status', 'description', 'assigned_to', 'department']:
                    old_val = getattr(old, field)
                    new_val = getattr(self, field)
                    if old_val != new_val:
                        changes[field] = {
                            'from': str(old_val) if old_val else None,
                            'to': str(new_val) if new_val else None
                        }
            except Grievance.DoesNotExist:
                is_new = True
        
        # Save first to ensure we have a PK
        super().save(*args, **kwargs)
        
        if changes:
            GrievanceLog.objects.create(
                user=getattr(self, 'last_updated_by', None),
                grievance=self,
                action='STATUS_CHANGE' if 'status' in changes else 'UPDATE',
                details=f"Grievance #{self.id} updated",
                previous_data=changes,
                new_data={k: v['to'] for k, v in changes.items()}
            )
            
            # Create notifications based on changes
            if 'status' in changes:
                if self.status == self.Status.RESOLVED:
                    Notification.objects.create(
                        user=self.user,
                        grievance=self,
                        notification_type=Notification.NotificationType.GRIEVANCE_RESOLVED
                    )
                elif self.status == self.Status.REJECTED:
                    Notification.objects.create(
                        user=self.user,
                        grievance=self,
                        notification_type=Notification.NotificationType.GRIEVANCE_REJECTED
                    )
                elif self.status == self.Status.ESCALATED:
                    Notification.objects.create(
                        user=self.assigned_to,
                        grievance=self,
                        notification_type=Notification.NotificationType.GRIEVANCE_ESCALATED
                    )
            
            if 'assigned_to' in changes and self.assigned_to:
                Notification.objects.create(
                    user=self.assigned_to,
                    grievance=self,
                    notification_type=Notification.NotificationType.GRIEVANCE_ASSIGNED
                )
        
        if is_new:
            GrievanceLog.objects.create(
                user=self.user,
                grievance=self,
                action='CREATE',
                details=f"Grievance #{self.id} created",
                new_data={
                    'status': self.status,
                    'description': self.description,
                    'issue_type': self.issue_type
                }
            )
            
    class Meta:
        verbose_name = "Grievance"
        verbose_name_plural = "Grievances"
        ordering = ['-created_at']

class GrievanceUpdate(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=Grievance.Status.choices)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Update for Grievance #{self.grievance.id}"

class Attachment(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='grievance_attachments/')
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for Grievance #{self.grievance.id}"

class Feedback(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='feedbacks')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_feedbacks')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    assigned_employee = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='employee_feedbacks'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"Feedback for Grievance #{self.grievance.id} - Rating: {self.rating}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            # Automatically set department and assigned employee from grievance
            self.department = self.grievance.department
            self.assigned_employee = self.grievance.assigned_to
            self.customer = self.grievance.user
        super().save(*args, **kwargs)

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        GRIEVANCE_ASSIGNED = 'GRIEVANCE_ASSIGNED', 'Grievance Assigned'
        GRIEVANCE_RESOLVED = 'GRIEVANCE_RESOLVED', 'Grievance Resolved'
        GRIEVANCE_REJECTED = 'GRIEVANCE_REJECTED', 'Grievance Rejected'
        GRIEVANCE_ESCALATED = 'GRIEVANCE_ESCALATED', 'Grievance Escalated'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - Grievance #{self.grievance.id}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            if self.notification_type == self.NotificationType.GRIEVANCE_ASSIGNED:
                self.message = f"You have been assigned to Grievance #{self.grievance.id}"
            elif self.notification_type == self.NotificationType.GRIEVANCE_RESOLVED:
                self.message = f"Your Grievance #{self.grievance.id} has been resolved"
            elif self.notification_type == self.NotificationType.GRIEVANCE_REJECTED:
                self.message = f"Your Grievance #{self.grievance.id} has been rejected"
            elif self.notification_type == self.NotificationType.GRIEVANCE_ESCALATED:
                self.message = f"Grievance #{self.grievance.id} has been escalated to you"
        super().save(*args, **kwargs)