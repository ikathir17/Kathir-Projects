from grievances.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        notifications = []
        unread_notifications_count = 0
    
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    } 