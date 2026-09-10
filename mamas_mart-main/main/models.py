from django.db import models
from django.utils import timezone
from products.models import Product
from inventory.models import Inventory

class DailySalesReport(models.Model):
    """
    Daily aggregated sales report for dashboard statistics
    """
    date = models.DateField(default=timezone.now)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_transactions = models.IntegerField(default=0)
    items_sold = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f"Sales Report for {self.date} - ${self.total_sales}"

class CategorySalesReport(models.Model):
    """
    Monthly sales report by product category
    """
    category = models.CharField(max_length=100)
    month = models.DateField()  # Will store first day of month
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    items_sold = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-month', '-total_sales']
        unique_together = ['category', 'month']

    def __str__(self):
        return f"{self.category} - {self.month.strftime('%B %Y')}"

class Supplier(models.Model):
    """
    Supplier information for purchase tracking
    """
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    

class Inventory(models.Model):
    """
    Inventory model to track stock items
    """
    item_name = models.CharField(max_length=200)
    category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_name']
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return self.item_name
    
    
class Sales(models.Model):
    """
    Sales model to track sales transactions
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Sale of {self.product.name} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"


class Purchase(models.Model):
    """
    Purchase model to track purchase transactions
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Purchase of {self.product.name} from {self.supplier.name if self.supplier else 'Unknown'} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"   