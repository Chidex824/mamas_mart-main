from django.db import models
from django.urls import reverse
from products.models import Product

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_in_sales')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

    def get_absolute_url(self):
        return reverse('sales:index')
