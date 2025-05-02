from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser, Department
from .utils import generate_captcha
import logging

logger = logging.getLogger(__name__)

def is_superuser(user):
    return user.is_superuser

def register_view(request):
    logger.info("Registration request received")
    if request.method == 'POST':
        logger.info("POST request received for registration")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            logger.info("Form is valid, processing registration")
            try:
                user = form.save(commit=False)
                logger.info(f"User object created: {user.username}")
                
                # Handle department assignment for employees
                if user.role == CustomUser.Role.EMPLOYEE:
                    user.department = form.cleaned_data['department']
                    logger.info(f"Department assigned: {user.department}")
                
                # Set admin permissions if role is ADMIN
                if user.role == CustomUser.Role.ADMIN:
                    # Only allow admin creation if current user is superuser
                    if not request.user.is_superuser:
                        logger.warning("Non-superuser attempted to create admin account")
                        messages.error(request, 'Only superusers can create admin accounts')
                        return redirect('register')
                    user.is_staff = True
                    user.is_superuser = True
                    logger.info("Admin permissions set")
                
                # Set initial verification status
                user.is_verified = False
                
                # Save the user
                user.save()
                logger.info(f"User saved to database: {user.username}")
                
                # Add to appropriate group
                if user.role == CustomUser.Role.ADMIN:
                    admin_group, _ = Group.objects.get_or_create(name='Admins')
                    user.groups.add(admin_group)
                    logger.info("Added to admin group")
                elif user.role == CustomUser.Role.EMPLOYEE:
                    employee_group, _ = Group.objects.get_or_create(name='Employees')
                    user.groups.add(employee_group)
                    logger.info("Added to employee group")
                
                # Log in the user
                login(request, user)
                logger.info(f"User logged in: {user.username}")
                
                # Send success message with role-specific information
                role_message = {
                    CustomUser.Role.ADMIN: 'Admin account created successfully!',
                    CustomUser.Role.EMPLOYEE: f'Employee account created successfully! You are assigned to {user.department.name} department.',
                    CustomUser.Role.CUSTOMER: 'Customer account created successfully! You can now submit grievances.'
                }
                messages.success(request, role_message[user.role])
                
                # Redirect based on role
                if user.role == CustomUser.Role.ADMIN:
                    return redirect('admin_dashboard')
                elif user.role == CustomUser.Role.EMPLOYEE:
                    return redirect('employee_dashboard')
                else:
                    return redirect('customer_dashboard')
                    
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}")
                messages.error(request, f'Error creating account: {str(e)}')
                return redirect('register')
        else:
            logger.error(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Remove ADMIN option from role choices for non-superusers
        initial_form = CustomUserCreationForm()
        if not request.user.is_superuser:
            initial_form.fields['role'].choices = [
                (role, label) 
                for role, label in CustomUser.Role.choices 
                if role != CustomUser.Role.ADMIN
            ]
    
    return render(request, 'users/register.html', {
        'form': initial_form if 'initial_form' in locals() else CustomUserCreationForm(),
        'roles': CustomUser.Role.choices
    })

@user_passes_test(is_superuser)
def register_admin_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            admin_group, _ = Group.objects.get_or_create(name='Admins')
            user.groups.add(admin_group)
            
            messages.success(request, 'Admin user created successfully!')
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm(initial={'role': CustomUser.Role.ADMIN})
    
    return render(request, 'users/register_admin.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            captcha = form.cleaned_data['captcha']
            
            # Verify CAPTCHA
            stored_captcha = request.session.get('captcha_text')
            if not stored_captcha or captcha.upper() != stored_captcha.upper():
                form.add_error('captcha', 'Invalid CAPTCHA')
                # Generate new CAPTCHA
                captcha_text, captcha_html = generate_captcha()
                request.session['captcha_text'] = captcha_text
                return render(request, 'users/login.html', {
                    'form': form,
                    'captcha_html': captcha_html
                })
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect based on role
                if user.role == CustomUser.Role.ADMIN or user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.role == CustomUser.Role.EMPLOYEE:
                    return redirect('employee_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    # Generate new CAPTCHA
    captcha_text, captcha_html = generate_captcha()
    request.session['captcha_text'] = captcha_text
    
    return render(request, 'users/login.html', {
        'form': form,
        'captcha_html': captcha_html
    })

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == CustomUser.Role.ADMIN or user.is_superuser:
        return redirect('admin_dashboard')
    elif user.role == CustomUser.Role.EMPLOYEE:
        return redirect('employee_dashboard')
    else:
        return redirect('customer_dashboard')