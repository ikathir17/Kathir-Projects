from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser, Department

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'required': 'required'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'required': 'required'}))
    phone = forms.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'required': 'required', 'placeholder': '+91XXXXXXXXXX'})
    )
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices, 
        required=True,
        widget=forms.Select(attrs={'required': 'required'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'department-field'})
    )
    

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'department', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required by default
        for field in self.fields:
            self.fields[field].required = True
        # Department is only required for employees
        self.fields['department'].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')
        
        # Department is required only for employees
        if role == CustomUser.Role.EMPLOYEE and not department:
            self.add_error('department', 'Department is required for employees')
        
        return cleaned_data
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        return phone
    
    
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-control'
    }))
    captcha = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter the CAPTCHA text',
        'class': 'form-control'
    }))