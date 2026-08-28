from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.add_inventory, name='add_inventory'),
    path('edit/<int:inventory_id>/', views.edit_inventory, name='edit_inventory'),
    path('delete/<int:inventory_id>/', views.delete_inventory, name='delete_inventory'),
    path('supplier/', views.supplier, name='supplier'),
    path('invoice/', views.invoice, name='invoice'),
    path('invoice/<int:sale_id>/', views.invoice, name='invoice_with_id'),
    path('warehouse/', views.warehouse, name='warehouse'),
    path('transfer_product/', views.transfer_product, name='transfer_product'),
    path('stock/', views.stock, name='stock'),
    path('view/<int:inventory_id>/', views.view_inventory, name='view_inventory'),
]
