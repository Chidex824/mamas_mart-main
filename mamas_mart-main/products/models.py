from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from accounts.models import User

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])

class Purchase(models.Model):
    """Purchase records for product restocking"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey('main.Supplier', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase of {self.quantity} {self.product.name} on {self.date.date()}"

class Sale(models.Model):
    """Individual sale records"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchases')
    date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales')

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Update product stock
        self.product.stock -= self.quantity
        self.product.save()

    def __str__(self):
        return f"Sale of {self.quantity} {self.product.name} on {self.date.date()}"
