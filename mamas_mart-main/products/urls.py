from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('table/', views.product_table, name='product_table'),
    path('add/', views.add_product, name='add_product'),
    path('<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('categories/', views.category_list, name='category_list'),
]