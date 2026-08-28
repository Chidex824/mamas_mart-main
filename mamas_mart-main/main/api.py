from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractWeek, ExtractMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import DailySalesReport
from products.models import Product, Purchase, Sale
from accounts.models import User
from sales.models import Sale as SaleModel

def get_dashboard_data():
    """Get all dashboard data in a single API call"""
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Weekly earnings data
    weekly_sales = DailySalesReport.objects.filter(
        date__gte=week_ago
    ).annotate(
        day=TruncDate('date')
    ).values('day').annotate(
        total=Sum('total_sales'),
        transactions=Count('id')
    ).order_by('day')

    # Monthly revenue breakup
    revenue_breakup = Sale.objects.filter(
        date__gte=month_ago
    ).values('product__category').annotate(
        total=Sum('total_amount')
    ).order_by('-total')

    # Sales vs Expenses overview
    sales_expenses = {
        'sales': [],
        'expenses': [],
        'dates': []
    }
    
    for i in range(8):  # Last 8 months
        date = now - timedelta(days=30 * i)
        month_sales = Sale.objects.filter(
            date__year=date.year,
            date__month=date.month
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        month_expenses = Purchase.objects.filter(
            date__year=date.year,
            date__month=date.month
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        sales_expenses['sales'].insert(0, float(month_sales))
        sales_expenses['expenses'].insert(0, float(month_expenses))
        sales_expenses['dates'].insert(0, date.strftime('%b'))

    # Get current stats
    current_stats = {
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lte=10).count(),
        'todays_sales': DailySalesReport.objects.filter(
            date=timezone.now().date()
        ).aggregate(
            total_sales=Sum('total_sales'),
            total_transactions=Count('id')
        ),
        'new_customers': User.objects.filter(date_joined__gte=week_ago).count(),
        'orders': SaleModel.objects.filter(date__gte=week_ago).count(),
        'completed': SaleModel.objects.filter(date__gte=week_ago, status='completed').count(),
        'cancelled': SaleModel.objects.filter(date__gte=week_ago, status='cancelled').count(),
        'refund_requests': SaleModel.objects.filter(date__gte=week_ago, status='refund_requested').count(),
    }

    return {
        'weekly_earnings': list(weekly_sales),
        'revenue_breakup': list(revenue_breakup),
        'sales_expenses': sales_expenses,
        'current_stats': current_stats
    }

def get_stock_report():
    """API to get stock report data"""
    products = Product.objects.all().values(
        'id', 'name', 'product_id', 'price', 'category__name', 'stock', 'status'
    )
    stock_list = []
    for p in products:
        stock_list.append({
            'id': p['id'],
            'items': p['name'],
            'product_id': p['product_id'],
            'price': p['price'],
            'category': p['category__name'],
            'quantity': p['stock'],
            'status': p['status'],
        })
    return stock_list

def get_top_selling_products():
    """API to get top selling products data"""
    sales = Sale.objects.values(
        'date', 'product__name', 'product__product_id', 'price', 'quantity', 'total_amount'
    ).order_by('-date')[:10]
    top_selling_list = []
    for s in sales:
        top_selling_list.append({
            'date': s['date'].strftime('%d/%m/%Y') if s['date'] else '',
            'items': s['product__name'],
            'product_id': s['product__product_id'],
            'price': s['price'],
            'sales': s['quantity'],
            'earnings': s['total_amount'],
        })
    return top_selling_list
