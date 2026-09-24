
from django.db import models
from products.models import Category

class Inventory(models.Model):
    item_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory/', blank=True, null=True)
    supplier = models.CharField(max_length=200)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            import random
            while True:
                candidate = f"INV{random.randint(100000, 999999)}"
                if not Inventory.objects.filter(barcode=candidate).exists():
                    self.barcode = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name

    @property
    def product_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-product.png'

