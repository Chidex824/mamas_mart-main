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
    Registration view with three scenarios:
    1. No users exist -> First user becomes admin (staff + superuser)
    2. Logged in staff -> Can create new staff accounts
    3. Other cases -> Can create regular staff account
    """
    # Check if this is the first user being created
    is_first_user = User.objects.count() == 0
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if is_first_user:
                user.is_staff = True
                user.is_superuser = True  # First user is admin
                user.save()
                login(request, user)  # Automatically log in the admin
                messages.success(request, 'Admin account created and logged in successfully!')
                return redirect('main:index')
            else:
                user.is_staff = True  # All users are staff by default
                # Generate a random password for the new staff user
                password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))
                user.set_password(password)
                user.save()
                # Send login details to the new staff user via email
                subject = 'Your Staff Account Details'
                message = f'Hello {user.first_name},\n\nYour staff account has been created.\nUsername: {user.username}\nPassword: {password}\n\nPlease log in and change your password immediately.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    messages.success(request, f'Staff account for {user.username} created successfully! Login details have been sent to their email.')
                except Exception as e:
                    messages.warning(request, f'Staff account for {user.username} created, but failed to send email. Please provide login details manually.')
                if request.user.is_authenticated:
                    return redirect('accounts:register')  # Stay on page for creating more staff
                return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'is_staff_registration': request.user.is_staff
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
        next_url = request.GET.get('next', '')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    
                    # Validate and sanitize the next URL
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
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'role']

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
    """View to list all users"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_add(request):
    """View to add a new user"""
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'User {user.username} was created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserManagementForm()
    
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Add'})

@login_required
def user_edit(request, pk):
    """View to edit an existing user"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'User {user.username} was updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserManagementForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Edit', 'user': user})

@login_required
def user_delete(request, pk):
    """View to delete a user"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} was deleted successfully.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@login_required
def user_management(request):
    return render(request, 'accounts/user_management.html')

from .forms import UserProfileForm, UserNotificationForm, UserPreferencesForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def settings_view(request):
    user = request.user
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
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
