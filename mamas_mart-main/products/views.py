from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, F, Q
from .models import Product, Category
from inventory.models import Inventory as InventoryItem
from decimal import Decimal

def staff_required(user):
    return user.is_staff

@login_required
def product_list(request):
    """Display list of all products with search and filter functionality."""
    # Handle POST request for adding new product
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            
        try:
            # Validate required fields
            required_fields = ['name', 'category', 'price', 'stock']
            for field in required_fields:
                if not request.POST.get(field):
                    return JsonResponse({
                        'success': False, 
                        'error': f'{field.title()} is required'
                    }, status=400)
            
            # Get form data
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            description = request.POST.get('description', '')
            is_available = request.POST.get('is_available') == 'on'  # checkbox value
            
            # Create new product
            product = Product.objects.create(
                name=name,
                category_id=category_id,
                price=price,
                stock=stock,
                description=description,
                is_available=is_available
            )
            
            # Handle image upload
            if request.FILES.get('image'):
                product.image = request.FILES['image']
                product.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # Get all products with category
    products = Product.objects.all().select_related('category')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(category__name__icontains=search_query)
        )

    # Category filter - this now handles the category nav item
    category = request.GET.get('category')
    if category == 'category':  # When category filter is active
        # You might want to customize this filter based on your needs
        products = products.order_by('category__name', 'name')
    
    # Stock/Availability filter
    stock_filter = request.GET.get('availability')
    if stock_filter == 'stock':  # When stock filter is active
        products = products.filter(stock__lte=10).order_by('stock')  # Show low stock items first
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10)  # Show 10 products per page
    try:
        products = paginator.get_page(page)
    except:
        products = paginator.get_page(1)  # Default to first page if there's an error

    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    # For AJAX requests, return only the table content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = 'products/includes/product_table.html'
    else:
        # For regular requests, also fetch inventory items for the modal
        used_names = Product.objects.values_list('name', flat=True)
        inventory_items = InventoryItem.objects.exclude(item_name__in=used_names)
        context = {
            'products': products,
            'categories': categories,
            'search_query': search_query,
            'inventory_items': inventory_items,
        }
        return render(request, 'products/product_list.html', context)
    
    return render(request, template, context)

@login_required
def add_product(request):
    """Add a new product from inventory only."""
    if request.method == 'POST':
        try:
            inventory_id = request.POST.get('inventory_item')
            inventory_item = InventoryItem.objects.get(id=inventory_id)
            category_id = inventory_item.category.id
            name = inventory_item.item_name
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            description = request.POST.get('description')
            is_available = request.POST.get('is_available') == 'on'
            product = Product.objects.create(
                name=name,
                category_id=category_id,
                price=price,
                stock=stock,
                description=description,
                is_available=is_available
            )
            if request.FILES.get('image'):
                product.image = request.FILES['image']
                product.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    # For GET request, render the add product modal with inventory items and categories
    # Only show inventory items not already used as products
    used_names = Product.objects.values_list('name', flat=True)
    inventory_items = InventoryItem.objects.exclude(item_name__in=used_names)
    categories = Category.objects.all()
    return render(request, 'products/includes/add_product_modal.html', {'categories': categories, 'inventory_items': inventory_items})

@login_required
def edit_product(request, product_id):
    """Edit an existing product."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            # Update product data
            product.name = request.POST.get('name')
            product.category_id = request.POST.get('category')
            product.price = request.POST.get('price')
            product.stock = request.POST.get('stock')
            product.description = request.POST.get('description')
            product.is_available = request.POST.get('is_available') == 'on'
            
            # Handle image upload
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            
            product.save()
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Return product data for GET request
    product_data = {
        'id': product.id,
        'name': product.name,
        'category': product.category_id,
        'price': str(product.price),
        'stock': product.stock,
        'description': product.description,
        'is_available': product.is_available,
        'image_url': product.image.url if product.image else None
    }
    
    return JsonResponse(product_data)

@login_required
def delete_product(request, product_id):
    """Delete a product."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def product_table(request):
    """Return either the product table content for AJAX requests or the full page for direct access."""
    products = Product.objects.all().select_related('category')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(category__name__icontains=search_query)
        )

    # Category filter
    category = request.GET.get('category')
    if category == 'category':
        products = products.order_by('category__name', 'name')
    
    # Stock filter
    stock_filter = request.GET.get('stock')
    if stock_filter == 'stock':
        products = products.filter(stock__lte=10).order_by('stock')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 10)
    try:
        products = paginator.get_page(page)
    except:
        products = paginator.get_page(1)

    # Get all categories for filter dropdown
    categories = Category.objects.all()

    # Prepare context
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'request': request
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # For AJAX requests from dashboard
        if request.GET.get('from_dashboard'):
            # Return simplified product table for dashboard integration
            return render(request, 'products/includes/product_table.html', context)
        # For regular AJAX requests from product page
        return render(request, 'products/includes/product_table.html', context)
    
    # For direct access, return the full page
    return render(request, 'products/product_list.html', context)

@login_required
def category_list(request):
    """Display and add product categories."""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name)
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

