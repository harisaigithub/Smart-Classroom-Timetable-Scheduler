from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    # Change '.order_with_respect_to' to '.order_by'
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark them as read
    notifications.update(is_read=True)
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })