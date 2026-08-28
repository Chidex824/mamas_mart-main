from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .api import get_dashboard_data, get_stock_report, get_top_selling_products

@login_required
def index(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON data for AJAX requests
        return JsonResponse(get_dashboard_data())
    
    # Initial page load - return basic template
    return render(request, 'main/index.html')

@login_required
def get_dashboard_updates(request):
    """API endpoint for getting dashboard updates"""
    return JsonResponse(get_dashboard_data())

@login_required
def stock_report_api(request):
    """API endpoint for stock report"""
    data = get_stock_report()
    return JsonResponse({'stock_report': data})

@login_required
def top_selling_products_api(request):
    """API endpoint for top selling products"""
    data = get_top_selling_products()
    return JsonResponse({'top_selling_products': data})




