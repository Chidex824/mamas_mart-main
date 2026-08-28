from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Sale
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from products.models import Product
from main.models import DailySalesReport

class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'

class SaleCreateView(CreateView):
    model = Sale
    template_name = 'sales/add_sales.html'
    fields = ['product', 'quantity', 'price']
    success_url = reverse_lazy('sales:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        sale = self.object
        # Deduct stock from product
        product = sale.product
        if product.stock >= sale.quantity:
            product.stock -= sale.quantity
            product.save()
        # Update dashboard stats
        today = sale.date
        report, created = DailySalesReport.objects.get_or_create(date=today)
        report.total_sales += sale.price * sale.quantity
        report.total_transactions += 1
        report.items_sold += sale.quantity
        report.save()
        return response

class SaleUpdateView(UpdateView):
    model = Sale
    template_name = 'sales/edit_sales.html'
    fields = ['product', 'quantity', 'price']
    success_url = reverse_lazy('sales:index')

    def form_valid(self, form):
        old_sale = Sale.objects.get(pk=self.object.pk)
        old_quantity = old_sale.quantity
        response = super().form_valid(form)
        sale = self.object
        product = sale.product
        # Adjust stock
        product.stock += old_quantity  # revert old sale
        if product.stock >= sale.quantity:
            product.stock -= sale.quantity
            product.save()
        # Update dashboard stats
        today = sale.date
        report, created = DailySalesReport.objects.get_or_create(date=today)
        report.total_sales += (sale.price * sale.quantity) - (old_sale.price * old_quantity)
        report.items_sold += sale.quantity - old_quantity
        report.save()
        return response

class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'sales/remove_sales.html'
    success_url = reverse_lazy('sales:index')

@csrf_exempt
def ajax_edit_sale(request, sale_id):
    if request.method == 'POST':
        sale = get_object_or_404(Sale, id=sale_id)
        quantity = int(request.POST.get('quantity', sale.quantity))
        price = request.POST.get('price', sale.price)
        sale.quantity = quantity
        sale.price = price
        sale.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def ajax_delete_sale(request, sale_id):
    if request.method == 'POST':
        sale = get_object_or_404(Sale, id=sale_id)
        sale.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
