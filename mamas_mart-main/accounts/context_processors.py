from .models import Notification, InternalMessage
from products.models import Product

def header_context(request):
    """
    Context processor providing notifications and messages to the shared header.
    """
    if not request.user.is_authenticated:
        return {}

    user = request.user

    # Fetch user notifications (direct or broadcast)
    notifications = Notification.objects.filter(
        recipient=user
    ) | Notification.objects.filter(recipient__isnull=True)
    notifications = notifications.distinct().order_by('-created_at')

    # Seed initial notifications if none exist for a friendly first-time experience
    if not notifications.exists():
        Notification.objects.create(
            recipient=user,
            title="Welcome to Mama's Mart",
            message="System is ready. You can manage products, track inventory, and view sales.",
            notification_type="info"
        )
        # Check for any low stock items
        low_stock = Product.objects.filter(stock__lte=5).first()
        if low_stock:
            Notification.objects.create(
                recipient=user,
                title="Low Stock Alert",
                message=f"Product '{low_stock.name}' has only {low_stock.stock} units remaining.",
                notification_type="warning",
                link="/products/"
            )
        notifications = Notification.objects.filter(
            recipient=user
        ) | Notification.objects.filter(recipient__isnull=True)
        notifications = notifications.distinct().order_by('-created_at')

    unread_notifications_count = notifications.filter(is_read=False).count()

    # Fetch user messages
    messages_qs = InternalMessage.objects.filter(
        recipient=user
    ) | InternalMessage.objects.filter(recipient__isnull=True)
    messages_qs = messages_qs.distinct().order_by('-created_at')

    unread_messages_count = messages_qs.filter(is_read=False).count()

    return {
        'header_notifications': notifications[:5],
        'unread_notifications_count': unread_notifications_count,
        'header_messages': messages_qs[:5],
        'unread_messages_count': unread_messages_count,
    }
