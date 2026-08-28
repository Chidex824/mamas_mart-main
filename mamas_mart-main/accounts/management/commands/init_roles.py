from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import Role, User
from accounts.permissions import ROLE_PERMISSIONS

class Command(BaseCommand):
    help = 'Initialize roles and permissions'

    def handle(self, *args, **kwargs):
        # Create roles
        roles = {
            Role.ADMIN: 'Administrator with full system access',
            Role.MANAGER: 'Manager with inventory and sales management access',
            Role.STAFF: 'Staff with basic inventory and sales access',
            Role.CASHIER: 'Cashier with sales processing access',
        }

        for role_name, description in roles.items():
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))

        # Assign permissions to roles
        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = Role.objects.get(name=role_name)
            
            # Get or create permissions
            for perm_codename in permissions:
                try:
                    perm = Permission.objects.get(codename=perm_codename)
                    role.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permission not found: {perm_codename}'))

            self.stdout.write(self.style.SUCCESS(f'Assigned permissions to role: {role_name}'))

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin',
                'admin@example.com',
                'admin123',
                role=Role.objects.get(name=Role.ADMIN)
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
