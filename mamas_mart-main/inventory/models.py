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
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
