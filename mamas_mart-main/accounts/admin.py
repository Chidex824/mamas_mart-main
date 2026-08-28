from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from .models import User, Role

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
        ('Roles and Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permissions')
    filter_horizontal = ('permissions',)
    
    def get_permissions(self, obj):
        return ", ".join([p.codename for p in obj.permissions.all()])
    get_permissions.short_description = 'Permissions'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission)
