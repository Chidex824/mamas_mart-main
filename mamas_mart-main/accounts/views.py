from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django import forms
from .models import User, Role
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    is_staff = forms.BooleanField(required=False, label='Register as staff member',
                                help_text='Check this to grant staff privileges')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control'
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name',
            'class': 'form-control'
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name',
            'class': 'form-control'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control',
            'id': 'password1'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'form-control',
            'id': 'password2'
        })
        self.fields['is_staff'].widget.attrs.update({
            'class': 'form-check-input'
        })
        
        # Show is_staff field only to staff users
        if not user or not user.is_staff:
            self.fields['is_staff'].widget = forms.HiddenInput()
            self.fields['is_staff'].initial = False
        
        # Remove help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None

import random
import string
from django.core.mail import send_mail
from django.conf import settings

def register(request):
    """
    Admin-only Registration view:
    1. No users exist -> First user onboarding (creates initial Admin).
    2. Admin user logged in -> Can register new staff/admin accounts with explicit password & role.
    3. Non-admin visitor -> Access restricted notice indicating only administrators can issue credentials.
    """
    is_first_user = User.objects.count() == 0
    is_admin = request.user.is_authenticated and (
        request.user.is_superuser or request.user.is_staff or (request.user.role and request.user.role.name == 'admin')
    )

    if not is_first_user and not is_admin:
        return render(request, 'accounts/register.html', {
            'is_allowed': False,
            'roles': Role.objects.all(),
        })

    roles = Role.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        role_id = request.POST.get('role')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/register.html', {'is_allowed': True, 'roles': roles, 'form_data': request.POST})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'is_allowed': True, 'roles': roles, 'form_data': request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Please choose another.")
            return render(request, 'accounts/register.html', {'is_allowed': True, 'roles': roles, 'form_data': request.POST})

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            is_staff=True
        )
        if is_first_user:
            user.is_superuser = True
            admin_role = Role.objects.filter(name=Role.ADMIN).first()
            if admin_role:
                user.role = admin_role

        if role_id:
            try:
                selected_role = Role.objects.get(id=role_id)
                user.role = selected_role
                if selected_role.name == Role.ADMIN:
                    user.is_superuser = True
            except Role.DoesNotExist:
                pass

        user.set_password(password)
        user.save()

        if is_first_user:
            login(request, user)
            messages.success(request, 'Initial Admin account created and logged in successfully!')
            return redirect('main:index')

        messages.success(request, f'Staff account for "{user.username}" created successfully with assigned role!')
        return redirect('accounts:user_list')

    return render(request, 'accounts/register.html', {
        'is_allowed': True,
        'is_first_user': is_first_user,
        'roles': roles,
    })

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

def login_view(request):
    """Handle user authentication and login."""
    if request.user.is_authenticated:
        return redirect('main:index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember', False)
        login_role = request.POST.get('login_role', 'staff')
        next_url = request.GET.get('next', '')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    if login_role == 'admin' and not (user.is_staff or user.is_superuser or (user.role and user.role.name == 'admin')):
                        messages.error(request, 'Account does not have administrative privileges. Please log in as Staff.')
                        return render(request, 'accounts/login.html', {'login_role': login_role})

                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)
                    
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                        return HttpResponseRedirect(next_url)
                    
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('main:index')
                else:
                    messages.error(request, 'Your account is inactive. Please contact the administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
                
    return render(request, 'accounts/login.html')

class UserManagementForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'is_active', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

@login_required
def user_list(request):
    """View to list all users (alias to user_management)"""
    return redirect('accounts:user_management')

@login_required
def user_add(request):
    """View to add a new user via AJAX or standard POST"""
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        role_id = request.POST.get('role')
        password = request.POST.get('password')

        if not username or not password:
            err = 'Username and password are required.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err}, status=400)
            messages.error(request, err)
            return redirect('accounts:user_management')

        if User.objects.filter(username=username).exists():
            err = f"Username '{username}' already exists."
            if is_ajax:
                return JsonResponse({'success': False, 'error': err}, status=400)
            messages.error(request, err)
            return redirect('accounts:user_management')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            is_staff=True,
            is_active=True
        )
        if role_id:
            try:
                selected_role = Role.objects.get(id=role_id)
                user.role = selected_role
                if selected_role.name == Role.ADMIN:
                    user.is_superuser = True
            except Role.DoesNotExist:
                pass

        user.set_password(password)
        user.save()

        if is_ajax:
            return JsonResponse({'success': True, 'message': f'User {user.username} created successfully.'})
        messages.success(request, f'User {user.username} created successfully.')
        return redirect('accounts:user_management')

    return redirect('accounts:user_management')

@login_required
def user_edit(request, pk):
    """View to edit an existing user via AJAX or standard POST"""
    user = get_object_or_404(User, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'GET' and is_ajax:
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role.id if user.role else '',
            'is_active': user.is_active,
        })

    if request.method == 'POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        phone_number = request.POST.get('phone_number', user.phone_number)
        role_id = request.POST.get('role')
        is_active = request.POST.get('is_active') in ['true', 'on', '1', True]
        password = request.POST.get('password')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.is_active = is_active

        if role_id:
            try:
                selected_role = Role.objects.get(id=role_id)
                user.role = selected_role
                if selected_role.name == Role.ADMIN:
                    user.is_superuser = True
            except Role.DoesNotExist:
                pass

        if password and password.strip():
            user.set_password(password.strip())

        user.save()

        if is_ajax:
            return JsonResponse({'success': True, 'message': f'User {user.username} updated successfully.'})
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('accounts:user_management')

    return redirect('accounts:user_management')

@login_required
def user_delete(request, pk):
    """View to delete a user"""
    user = get_object_or_404(User, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.user.pk == user.pk:
        err = "You cannot delete your own logged-in account."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err}, status=400)
        messages.error(request, err)
        return redirect('accounts:user_management')

    if request.method == 'POST':
        username = user.username
        user.delete()
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'User {username} deleted successfully.'})
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('accounts:user_management')

    if is_ajax:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    return redirect('accounts:user_management')

@login_required
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    roles = Role.objects.all()
    return render(request, 'accounts/user_management.html', {
        'users': users,
        'roles': roles,
    })

from .forms import UserProfileForm, UserNotificationForm, UserPreferencesForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def settings_view(request):
    user = request.user
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        notification_form = UserNotificationForm(request.POST)
        preferences_form = UserPreferencesForm(request.POST)

        if (profile_form.is_valid() and password_form.is_valid() and
            notification_form.is_valid() and preferences_form.is_valid()):
            profile_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Important!

            # Here you would save notification and preferences data to user profile or related models
            # For now, just print or pass as this is a placeholder
            email_notifications = notification_form.cleaned_data['email_notifications']
            sms_notifications = notification_form.cleaned_data['sms_notifications']
            language = preferences_form.cleaned_data['language']
            timezone = preferences_form.cleaned_data['timezone']

            # TODO: Save these preferences to user profile or related model

            messages.success(request, 'Your settings have been updated successfully.')
            return redirect('accounts:settings')
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user)
        notification_form = UserNotificationForm()
        preferences_form = UserPreferencesForm()

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'notification_form': notification_form,
        'preferences_form': preferences_form,
    }
    return render(request, 'accounts/settings.html', context)


@login_required
def profile_view(request):
    """View to display and manage user profile and credentials."""
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            first_name = request.POST.get('first_name', user.first_name)
            last_name = request.POST.get('last_name', user.last_name)
            email = request.POST.get('email', user.email)
            phone_number = request.POST.get('phone_number', user.phone_number)
            address = request.POST.get('address', user.address)
            
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone_number
            user.address = address

            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']

            user.save()
            messages.success(request, 'Your profile details have been updated successfully.')
            return redirect('accounts:profile')

        elif action == 'change_password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('accounts:profile')
            else:
                for error_list in password_form.errors.values():
                    for err in error_list:
                        messages.error(request, err)
                return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'user': user})


@login_required
def notifications_view(request):
    """Independent notification center view."""
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            Notification.objects.filter(recipient=user).update(is_read=True)
            Notification.objects.filter(recipient__isnull=True).update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
            return redirect('accounts:notifications')

    notifications = Notification.objects.filter(
        recipient=user
    ) | Notification.objects.filter(recipient__isnull=True)
    notifications = notifications.distinct().order_by('-created_at')

    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
    })


@login_required
def messages_view(request):
    """Independent staff internal messaging view."""
    user = request.user

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()

        if subject and body:
            recipient = None
            if recipient_id and recipient_id != 'all':
                recipient = User.objects.filter(id=recipient_id).first()

            InternalMessage.objects.create(
                sender=user,
                recipient=recipient,
                subject=subject,
                body=body
            )
            messages.success(request, 'Staff message sent successfully.')
            return redirect('accounts:messages')
        else:
            messages.error(request, 'Subject and message body are required.')

    inbox_messages = InternalMessage.objects.filter(
        recipient=user
    ) | InternalMessage.objects.filter(recipient__isnull=True)
    inbox_messages = inbox_messages.distinct().order_by('-created_at')

    sent_messages = InternalMessage.objects.filter(sender=user).order_by('-created_at')
    staff_users = User.objects.all().order_by('username')

    return render(request, 'accounts/messages.html', {
        'inbox_messages': inbox_messages,
        'sent_messages': sent_messages,
        'staff_users': staff_users,
    })

