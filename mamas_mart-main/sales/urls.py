from django.urls import path
from .views import SaleListView, SaleCreateView, SaleUpdateView, SaleDeleteView
from . import views

app_name = 'sales'

urlpatterns = [
    path('', SaleListView.as_view(), name='index'),
    path('add/', SaleCreateView.as_view(), name='add'),
    path('edit/<int:pk>/', SaleUpdateView.as_view(), name='edit'),
    path('remove/<int:pk>/', SaleDeleteView.as_view(), name='remove'),
    path('edit/<int:sale_id>/', views.ajax_edit_sale, name='ajax_edit_sale'),
    path('delete/<int:sale_id>/', views.ajax_delete_sale, name='ajax_delete_sale'),
]
