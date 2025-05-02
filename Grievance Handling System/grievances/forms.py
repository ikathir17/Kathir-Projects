from django import forms
from .models import Grievance, Attachment

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ('issue_type', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ('file',)

class GrievanceStatusForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ('status',)