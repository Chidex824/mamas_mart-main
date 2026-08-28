from django.db import models
from django.utils import timezone
from products.models import Product

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