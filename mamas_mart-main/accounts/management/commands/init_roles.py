from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import Role, User
from accounts.permissions import ROLE_PERMISSIONS

# Safely import future models if defined in accounts.models
try:
    from accounts.models import Level, KPIS
except ImportError:
    Level = None
    KPIS = None


class Command(BaseCommand):
    help = 'Initialize levels, roles, system permissions and primary kpis in ims'

    def handle(self, *args, **kwargs):
        # 1. Initialize Levels (if Level model exists)
        levels = {
            'EXECUTIVE': 'Executive level with strategic oversight',
            'MANAGEMENT': 'Management level with departmental oversight',
            'OPERATIONS': 'Operations level with daily operational access',
            'SALES': 'Sales level with customer and POS access',
            'ACCOUNT': 'Accounting level with financial records access',
        }
        if Level is not None:
            for level_name, description in levels.items():
                level_obj, created = Level.objects.get_or_create(name=level_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created level: {level_name}'))

        # 2. Create Roles
        roles = {
            Role.ADMIN: 'Chief Operations and Supply Officer (COSO) - Full system access',
            Role.MANAGER: 'Inventory and Category Manager - Inventory and sales management',
            Role.STAFF: 'Logistics Manager - Inventory and operational access',
            Role.CASHIER: 'Store Accountant - Sales and cashier processing access',
        }

        for role_name, description in roles.items():
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created role: {role_name}'))

        # 3. Assign permissions to roles
        for role_name, permissions in ROLE_PERMISSIONS.items():
            try:
                role = Role.objects.get(name=role_name)
                for perm_codename in permissions:
                    try:
                        perm = Permission.objects.get(codename=perm_codename)
                        role.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Permission not found: {perm_codename}'))
                self.stdout.write(self.style.SUCCESS(f'Assigned permissions to role: {role_name}'))
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Role {role_name} not found'))

        # 4. Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_role = Role.objects.filter(name=Role.ADMIN).first()
            User.objects.create_superuser(
                'admin',
                'admin@example.com',
                'admin123',
                role=admin_role
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))

        # 5. Create Primary KPIs (if KPIS model exists)
        if KPIS is not None:
            kpis = {
                'SALES_GROWTH': 'Percentage increase in sales revenue over a period.',
                'MARKET_SHARE': 'Portion of total sales in a market captured by the company.',
                'CUSTOMER_ACQUISITION_COST': 'Cost to acquire a new customer.',
                'CUSTOMER_LIFETIME_VALUE': 'Total revenue a business can expect from a single customer account.',
                'RETURN_ON_INVESTMENT': 'Ratio of profit to investment.',
                'NET_PROFIT_MARGIN': 'Net profit as a percentage of revenue.',
                'OPERATING_EXPENSE_RATIO': 'Operating expenses as a percentage of revenue.',
                'INVENTORY_TURNOVER': 'Number of times inventory is sold and replaced over a period.',
                'STOCKOUT_RATE': 'Percentage of customer orders that cannot be filled due to lack of inventory.',
                'EMPLOYEE_TURNOVER': 'Rate at which employees leave the company.',
                'CUSTOMER_SATISFACTION_SCORE': 'Measure of customer satisfaction with products or services.',
            }
            for kpi_name, description in kpis.items():
                kpi, created = KPIS.objects.get_or_create(name=kpi_name, defaults={'description': description})
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created KPI: {kpi_name}'))
