from django.db.models import Q, Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Grievance, GrievanceLog, GrievanceUpdate, Attachment, Feedback, Notification
from .forms import GrievanceForm, AttachmentForm, GrievanceStatusForm
from users.models import CustomUser, Department
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

@login_required
def admin_dashboard(request):
    if not request.user.role == CustomUser.Role.ADMIN:
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        grievance_id = request.POST.get('grievance_id')
        employee_id = request.POST.get('employee_id')
        department_id = request.POST.get('department_id')
        
        try:
            grievance = Grievance.objects.get(id=grievance_id)
            
            if department_id:
                department = Department.objects.get(id=department_id)
                grievance.department = department
                grievance.assigned_to = None  # Reset assignment when department changes
                grievance.save()
                
                GrievanceUpdate.objects.create(
                    grievance=grievance,
                    updated_by=request.user,
                    status=grievance.status,
                    comment=f"Assigned to {department.name} department"
                )
                messages.success(request, f"Department assigned successfully!")
            
            if employee_id:
                employee = CustomUser.objects.get(id=employee_id)
                if grievance.department != employee.department:
                    messages.error(request, "Employee must be from the selected department")
                else:
                    grievance.assigned_to = employee
                    grievance.save()
                    
                    GrievanceUpdate.objects.create(
                        grievance=grievance,
                        updated_by=request.user,
                        status=grievance.status,
                        comment=f"Assigned to {employee.get_full_name()}"
                    )
                    messages.success(request, "Employee assigned successfully!")
            
            return redirect('admin_dashboard')
        
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('admin_dashboard')
    
    # Get all grievances with filters
    grievances = Grievance.objects.all()

    # Apply status filter
    status_filter = request.GET.get('status')
    if status_filter:
        grievances = grievances.filter(status=status_filter)

    # Apply date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        grievances = grievances.filter(created_at__date__gte=start_date)
    if end_date:
        grievances = grievances.filter(created_at__date__lte=end_date)

    # Order by creation date
    grievances = grievances.order_by('-created_at')
    
    departments = Department.objects.all()
    
    # Calculate statistics for dashboard
    total_grievances = grievances.count()
    resolved_grievances = grievances.filter(status=Grievance.Status.RESOLVED).count()
    in_progress_grievances = grievances.filter(status=Grievance.Status.IN_PROGRESS).count()
    escalated_grievances = grievances.filter(status=Grievance.Status.ESCALATED).count()
    rejected_grievances = grievances.filter(status=Grievance.Status.REJECTED).count()
    
    # Prepare employees by department
    employees_by_dept = {
        dept.id: dept.department_employees.filter(role=CustomUser.Role.EMPLOYEE)
        for dept in departments
    }
    
    # Pagination
    paginator = Paginator(grievances, 25)  # Show 25 grievances per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stats for the chart
    stats = {
        'total': total_grievances,
        'resolved': resolved_grievances,
        'in_progress': in_progress_grievances,
        'escalated': escalated_grievances,
        'rejected': rejected_grievances,
    }

    return render(request, 'grievances/admin_dashboard.html', {
        'stats': stats,
        'page_obj': page_obj,
        'is_paginated': True,
        'grievances': page_obj,
        'departments': departments,
        'employees_by_dept': employees_by_dept,
        'selected_status': status_filter,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def employee_dashboard(request):
    if not request.user.role == CustomUser.Role.EMPLOYEE:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Get assigned grievances
    assigned_grievances = Grievance.objects.filter(assigned_to=request.user)
    
    # Calculate counts
    in_progress_count = assigned_grievances.filter(status=Grievance.Status.IN_PROGRESS).count()
    resolved_count = assigned_grievances.filter(status=Grievance.Status.RESOLVED).count()
    
    # Handle status updates
    if request.method == 'POST':
        grievance_id = request.POST.get('grievance_id')
        new_status = request.POST.get('status')
        
        try:
            grievance = Grievance.objects.get(id=grievance_id, assigned_to=request.user)
            grievance.status = new_status
            grievance.save()
            
            # Create status update
            GrievanceUpdate.objects.create(
                grievance=grievance,
                updated_by=request.user,
                status=new_status,
                comment=f"Status changed to {grievance.get_status_display()}"
            )
            
            messages.success(request, 'Grievance status updated successfully!')
        except Grievance.DoesNotExist:
            messages.error(request, 'Grievance not found or you are not assigned to it.')
    
    return render(request, 'grievances/employee_dashboard.html', {
        'assigned_grievances': assigned_grievances,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count
    })

@login_required
def customer_dashboard(request):
    # Get all grievances for the current user
    grievances = Grievance.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate counts
    in_progress_count = grievances.filter(status=Grievance.Status.IN_PROGRESS).count()
    resolved_count = grievances.filter(status=Grievance.Status.RESOLVED).count()
    
    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            try:
                grievance = form.save(commit=False)
                grievance.user = request.user
                grievance.status = Grievance.Status.RECEIVED
                grievance.save()
                
                # Create log entry
                GrievanceLog.objects.create(
                    user=request.user,
                    grievance=grievance,
                    action='CREATE',
                    details=f"Grievance #{grievance.id} created"
                )
                
                messages.success(request, "Grievance submitted successfully!")
                return redirect('customer_dashboard')
            except Exception as e:
                messages.error(request, f"Error submitting grievance: {str(e)}")
    else:
        form = GrievanceForm()
    
    return render(request, 'grievances/customer_dashboard.html', {
        'form': form,
        'grievances': grievances,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count
    })

@login_required
def grievance_detail(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)
    updates = GrievanceUpdate.objects.filter(grievance=grievance).order_by('-created_at')
    
    # Mark all notifications for this grievance as read
    Notification.objects.filter(
        user=request.user,
        grievance=grievance,
        is_read=False
    ).update(is_read=True)
    
    # Check permissions - admin is treated as superuser
    if (request.user != grievance.user and 
        request.user != grievance.assigned_to and 
        request.user.role != CustomUser.Role.ADMIN):
        return HttpResponseForbidden("Access denied")
    
    # For employees, prevent editing if escalated
    if (request.user.role == CustomUser.Role.EMPLOYEE and 
        grievance.status == Grievance.Status.ESCALATED):
        return HttpResponseForbidden("Cannot modify escalated grievances")
    
    if request.method == 'POST':
        form = GrievanceStatusForm(request.POST, instance=grievance)
        if form.is_valid():
            old_status = grievance.status
            grievance = form.save(commit=False)
            grievance.last_updated_by = request.user
            grievance.save()
            
            if old_status != grievance.status:
                # Create status update
                GrievanceUpdate.objects.create(
                    grievance=grievance,
                    updated_by=request.user,
                    status=grievance.status,
                    comment=f"Status changed from {old_status} to {grievance.status}"
                )
                
                # Create notifications based on status change and user roles
                if grievance.status == Grievance.Status.IN_PROGRESS and grievance.assigned_to:
                    # Notify assigned employee
                    if not Notification.objects.filter(
                        user=grievance.assigned_to,
                        grievance=grievance,
                        is_read=False
                    ).exists():
                        Notification.objects.create(
                            user=grievance.assigned_to,
                            grievance=grievance,
                            message=f"You have been assigned to Grievance #{grievance.id}"
                        )
                elif grievance.status == Grievance.Status.RESOLVED:
                    # Notify customer about resolution
                    if not Notification.objects.filter(
                        user=grievance.user,
                        grievance=grievance,
                        is_read=False
                    ).exists():
                        Notification.objects.create(
                            user=grievance.user,
                            grievance=grievance,
                            message=f"Your Grievance #{grievance.id} has been resolved"
                        )
                elif grievance.status == Grievance.Status.REJECTED:
                    # Notify customer about rejection
                    if not Notification.objects.filter(
                        user=grievance.user,
                        grievance=grievance,
                        is_read=False
                    ).exists():
                        Notification.objects.create(
                            user=grievance.user,
                            grievance=grievance,
                            message=f"Your Grievance #{grievance.id} has been rejected"
                        )
                
                messages.success(request, "Status updated successfully!")
            return redirect('grievance_detail', pk=pk)
    else:
        form = GrievanceStatusForm(instance=grievance)
    
    return render(request, 'grievances/grievance_detail.html', {
        'grievance': grievance,
        'updates': updates,
        'form': form,
    })

@login_required
def grievance_logs(request):
    if request.user.is_superuser:
        logs = GrievanceLog.objects.all().order_by('-timestamp')
    else:
        logs = GrievanceLog.objects.filter(
            Q(user=request.user) | 
            Q(grievance__user=request.user)
        ).distinct().order_by('-timestamp')
    
    return render(request, 'grievances/logs.html', {'logs': logs})

@login_required
def admin_grievance_logs(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    logs = GrievanceLog.objects.all().select_related('user', 'grievance').order_by('-timestamp')
    
    # Add filters if needed
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    return render(request, 'grievances/admin_logs.html', {
        'logs': logs,
        'action_choices': GrievanceLog.ACTION_CHOICES
    })

@login_required
def delete_grievance(request, pk):
    try:
        grievance = Grievance.objects.get(pk=pk)
        
        # Check permissions
        if grievance.status in ['RESOLVED', 'REJECTED']:
            GrievanceLog.objects.create(
                user=request.user,
                grievance=grievance,
                action='DELETE_ATTEMPT',
                details=f"Attempted to delete grievance #{grievance.id} (status: {grievance.status})"
            )
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete resolved or rejected grievances'
            }, status=403)

        if not request.user.is_superuser and request.user != grievance.user:
            return JsonResponse({
                'success': False, 
                'error': 'You can only delete your own grievances'
            }, status=403)

        # Create log before deletion
        GrievanceLog.objects.create(
            user=request.user,
            grievance=grievance,
            action='DELETE',
            details=f"Grievance #{grievance.id} deleted"
        )
        
        grievance.delete()
        return JsonResponse({'success': True, 'message': 'Grievance deleted successfully'})
    
    except Grievance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Grievance not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def get_employees_by_department(request):
    try:
        department_id = request.GET.get('department')
        if department_id:
            employees = CustomUser.objects.filter(
                role=CustomUser.Role.EMPLOYEE,
                department_id=department_id
            ).values('id', 'first_name', 'last_name')
            
            employees_list = [{
                'id': emp['id'],
                'name': f"{emp['first_name']} {emp['last_name']}"
            } for emp in employees]
            
            return JsonResponse({'employees': employees_list})
        return JsonResponse({'employees': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def escalated_grievances(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied")
    
    # Handle POST requests for department and employee assignments
    if request.method == 'POST':
        grievance_id = request.POST.get('grievance_id')
        employee_id = request.POST.get('employee_id')
        department_id = request.POST.get('department_id')
        
        try:
            grievance = Grievance.objects.get(id=grievance_id)
            
            if department_id:
                department = Department.objects.get(id=department_id)
                grievance.department = department
                grievance.assigned_to = None  # Reset assignment when department changes
                grievance.save()
                
                GrievanceUpdate.objects.create(
                    grievance=grievance,
                    updated_by=request.user,
                    status=grievance.status,
                    comment=f"Assigned to {department.name} department"
                )
                messages.success(request, f"Department assigned successfully!")
            
            if employee_id:
                employee = CustomUser.objects.get(id=employee_id)
                if grievance.department != employee.department:
                    messages.error(request, "Employee must be from the selected department")
                else:
                    grievance.assigned_to = employee
                    grievance.save()
                    
                    GrievanceUpdate.objects.create(
                        grievance=grievance,
                        updated_by=request.user,
                        status=grievance.status,
                        comment=f"Assigned to {employee.get_full_name()}"
                    )
                    messages.success(request, "Employee assigned successfully!")
            
            return redirect('escalated_grievances')
        
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('escalated_grievances')
    
    # Get only escalated grievances
    grievances = Grievance.objects.filter(status=Grievance.Status.ESCALATED).order_by('-created_at')
    departments = Department.objects.all()
    
    # Calculate statistics
    stats = {
        'escalated': grievances.count()
    }
    
    # Prepare employees by department
    employees_by_dept = {
        dept.id: dept.department_employees.filter(role=CustomUser.Role.EMPLOYEE)
        for dept in departments
    }
    
    paginator = Paginator(grievances, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'grievances/escalated_grievances.html', {
        'stats': stats,
        'page_obj': page_obj,
        'is_paginated': True,
        'grievances': page_obj,
        'departments': departments,
        'employees_by_dept': employees_by_dept
    })

@login_required
def reviews(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    feedbacks = Feedback.objects.select_related('grievance', 'customer', 'department', 'assigned_employee').all()
    
    # Apply filters
    rating_filter = request.GET.get('rating')
    if rating_filter:
        feedbacks = feedbacks.filter(rating=rating_filter)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        feedbacks = feedbacks.filter(created_at__date__gte=start_date)
    if end_date:
        feedbacks = feedbacks.filter(created_at__date__lte=end_date)
    
    # Calculate statistics
    total_feedbacks = feedbacks.count()
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_distribution = {
        i: feedbacks.filter(rating=i).count()
        for i in range(1, 6)
    }
    
    # Department-wise average ratings
    dept_ratings = feedbacks.values('department__name').annotate(
        avg_rating=Avg('rating'),
        count=Count('id')
    ).order_by('-avg_rating')
    
    # Pagination
    paginator = Paginator(feedbacks, 25)  # Show 25 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedbacks': page_obj,
        'total_feedbacks': total_feedbacks,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'dept_ratings': dept_ratings,
        'is_paginated': True,
        'page_obj': page_obj,
        'selected_rating': rating_filter,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'grievances/reviews.html', context)

@login_required
def submit_feedback(request, grievance_id):
    grievance = get_object_or_404(
        Grievance, 
        id=grievance_id, 
        user=request.user, 
        status='RESOLVED'
    )
    
    # Check if feedback already exists
    if Feedback.objects.filter(grievance=grievance).exists():
        messages.error(request, 'Feedback has already been submitted for this grievance.')
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    # The save method will automatically set customer, department, and assigned_employee
                    Feedback.objects.create(
                        grievance=grievance,
                        rating=rating,
                        comment=comment
                    )
                    messages.success(request, 'Thank you for your feedback!')
                    return redirect('customer_dashboard')
                else:
                    messages.error(request, 'Rating must be between 1 and 5.')
            except ValueError:
                messages.error(request, 'Invalid rating value.')
        else:
            messages.error(request, 'Please provide a rating.')
    
    context = {
        'grievance': grievance,
        'department_name': grievance.department.name,
        'assigned_to_name': grievance.assigned_to.get_full_name() or grievance.assigned_to.username
    }
    return render(request, 'grievances/submit_feedback.html', context)

@login_required
def profile(request):
    return render(request, 'grievances/profile.html')

@login_required
def get_notifications(request):
    # Get base queryset
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter notifications based on user role
    if request.user.role == CustomUser.Role.EMPLOYEE:
        # Employee only sees notifications for grievances assigned to them
        notifications = notifications.filter(
            grievance__assigned_to=request.user,
            grievance__status=Grievance.Status.IN_PROGRESS
        ).order_by('-created_at')[:10]
    else:
        # Customer only sees resolved/rejected notifications for their own grievances
        notifications = notifications.filter(
            grievance__user=request.user,
            grievance__status__in=[Grievance.Status.RESOLVED, Grievance.Status.REJECTED]
        ).order_by('-created_at')[:10]
    
    # Get unread count for the filtered notifications
    unread_count = notifications.filter(is_read=False).count()
    
    return JsonResponse({
        'notifications': [
            {
                'id': notification.id,
                'message': notification.message,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'grievance_id': notification.grievance.id
            }
            for notification in notifications
        ],
        'unread_count': unread_count
    })

@login_required
@require_POST
@csrf_exempt
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        
        # Get fresh count after update
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count,
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)

@login_required
@require_POST
@csrf_exempt
def mark_all_notifications_read(request):
    # Only update notifications that are unread
    updated_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'unread_count': 0,
        'message': f'Marked {updated_count} notifications as read'
    })