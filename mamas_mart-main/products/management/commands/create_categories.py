from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Create initial product categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets'
            },
            {
                'name': 'Cosmetics',
                'description': 'Beauty and personal care products'
            },
            {
                'name': 'Smartphones',
                'description': 'Mobile phones and accessories'
            },
            {
                'name': 'Clothing',
                'description': 'Apparel and fashion items'
            },
            {
                'name': 'Accessories',
                'description': 'Fashion accessories and jewelry'
            },
            {
                'name': 'Appliances',
                'description': 'Home and kitchen appliances'
            },
            {
                'name': 'Computing',
                'description': 'Computers, laptops, and accessories'
            },
            {
                'name': 'Gaming',
                'description': 'Video games and gaming accessories'
            },
            {
                'name': 'Home & Living',
                'description': 'Home decor and furniture'
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Sports equipment and fitness gear'
            },
            {
                'name': 'Books & Media',
                'description': 'Books, music, and entertainment'
            },
            {
                'name': 'Health & Wellness',
                'description': 'Health supplements and medical supplies'
            },
            {
                'name': 'Automotive',
                'description': 'Car parts and accessories'
            },
            {
                'name': 'Baby & Kids',
                'description': 'Products for babies and children'
            },
            {
                'name': 'Groceries',
                'description': 'Food and household supplies'
            }
        ]

        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description']
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created category "{category_data["name"]}"')
            )
