from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

class UserNotificationForm(forms.Form):
    email_notifications = forms.BooleanField(required=False, label='Email Notifications')
    sms_notifications = forms.BooleanField(required=False, label='SMS Notifications')

class UserPreferencesForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        # Add more languages as needed
    ]
    TIMEZONE_CHOICES = [
        ('UTC', 'UTC'),
        ('EST', 'Eastern Standard Time'),
        ('PST', 'Pacific Standard Time'),
        # Add more timezones as needed
    ]
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True, label='Language')
    timezone = forms.ChoiceField(choices=TIMEZONE_CHOICES, required=True, label='Timezone')
