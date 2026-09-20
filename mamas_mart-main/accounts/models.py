from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Department model for staff assignment
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Custom roles for users
    """
    ADMIN = 'admin'
    MANAGER = 'manager'
    STAFF = 'staff'
    CASHIER = 'cashier'

    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (MANAGER, 'Manager'),
        (STAFF, 'Staff'),
        (CASHIER, 'Cashier'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')


class User(AbstractUser):
    """
    Custom user model with role-based permissions
    """
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    class Meta:
        permissions = [
            ("can_view_dashboard", "Can view dashboard"),
            ("can_manage_inventory", "Can manage inventory"),
            ("can_manage_sales", "Can manage sales"),
            ("can_manage_purchases", "Can manage purchases"),
            ("can_manage_users", "Can manage users"),
            ("can_view_reports", "Can view reports"),
            ("can_process_sales", "Can process sales"),
        ]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    Independent system and staff notifications
    """
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('danger', 'Urgent / Danger'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Recipient user, or null if broadcast to all staff"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient or 'All'}"


class InternalMessage(models.Model):
    """
    Independent internal messaging between staff and admin
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,
        blank=True,
        help_text="Recipient staff user"
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} (from {self.sender} to {self.recipient or 'All'})"

