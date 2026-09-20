from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Inventory
from django.urls import reverse
from django.contrib import messages
from products.models import Purchase, Category as ProductCategory
from main.models import Supplier
from collections import defaultdict
from sales.models import Sale
from decimal import Decimal, InvalidOperation

DEFAULT_CATEGORIES = ['Groceries', 'Beverages', 'Fresh Produce', 'Household Items', 'Personal Care', 'General']

def ensure_default_categories():
    if not ProductCategory.objects.exists():
        for cat_name in DEFAULT_CATEGORIES:
            ProductCategory.objects.get_or_create(name=cat_name)

def inventory_list(request):
    ensure_default_categories()
    inventories = Inventory.objects.select_related('category').all()
    categories = ProductCategory.objects.all()
    return render(request, 'inventory/inventory_list.html', {
        'inventories': inventories,
        'categories': categories,
    })

def add_inventory(request):
    ensure_default_categories()
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json'
        item_name = request.POST.get('item_name', '').strip()
        category_input = request.POST.get('category', '').strip()
        supplier_name = request.POST.get('supplier', '').strip()
        quantity = request.POST.get('quantity', '').strip()
        location = request.POST.get('location', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')

        if not all([item_name, category_input, supplier_name, quantity, location, price]):
            err = 'Complete all required inventory fields (Item Name, Category, Supplier, Price, Quantity, Location) before saving.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err}, status=400)
            messages.error(request, err)
            return redirect(reverse('inventory:inventory_list'))

        try:
            if category_input.isdigit():
                category = ProductCategory.objects.get(id=int(category_input))
            else:
                category, _ = ProductCategory.objects.get_or_create(name=category_input)
            
            quantity_value = int(quantity)
            price_value = Decimal(price)
            if quantity_value < 0 or price_value < 0:
                raise ValueError
        except (ProductCategory.DoesNotExist, ValueError, TypeError, InvalidOperation):
            err = 'Choose a valid category and enter valid non-negative quantity and price values.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err}, status=400)
            messages.error(request, err)
            return redirect(reverse('inventory:inventory_list'))

        inventory = Inventory.objects.create(
            item_name=item_name,
            category=category,
            supplier=supplier_name,
            quantity=quantity_value,
            location=location,
            price=price_value,
            description=description,
            image=image
        )
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Inventory item added successfully.'})
        messages.success(request, 'Inventory item added successfully.')
        return redirect(reverse('inventory:inventory_list'))

    return render(request, 'inventory/add_inventory.html', {'categories': categories})

def edit_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    categories = ProductCategory.objects.all()

    if request.method == 'POST':
        inventory.item_name = request.POST.get('item_name')
        category_id = request.POST.get('category')
        inventory.category = get_object_or_404(ProductCategory, id=category_id)
        inventory.supplier = request.POST.get('supplier')
        inventory.quantity = request.POST.get('quantity')
        inventory.location = request.POST.get('location')
        inventory.price = request.POST.get('price')
        inventory.description = request.POST.get('description')
        image = request.FILES.get('image')
        if image:
            inventory.image = image
        inventory.save()
        messages.success(request, 'Inventory item updated successfully.')
        return redirect(reverse('inventory:inventory_list'))

    return render(request, 'inventory/edit_inventory.html', {'inventory': inventory, 'categories': categories})

def delete_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    if request.method == 'POST':
        inventory.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect(reverse('inventory:inventory_list'))
    return render(request, 'inventory/delete_inventory.html', {'inventory': inventory})

def warehouse(request):
    inventories = Inventory.objects.select_related('category').all()
    location_dict = defaultdict(list)
    for inventory in inventories:
        location_dict[inventory.location].append(inventory)
    # Convert defaultdict to regular dict for template context
    grouped_inventories = dict(location_dict)
    return render(request, 'inventory/warehouse.html', {'grouped_inventories': grouped_inventories})

def supplier(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier.html', {'suppliers': suppliers})

def invoice(request, sale_id=None):
    sale = None
    if sale_id:
        sale = get_object_or_404(Sale, id=sale_id)
    purchases = Purchase.objects.select_related('product', 'supplier').all()
    return render(request, 'inventory/invoice.html', {'purchases': purchases, 'sale': sale})

def transfer_product(request):
    return render(request, 'inventory/transfer_product.html')

def stock(request):
    return render(request, 'inventory/stock.html')

def view_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    return render(request, 'inventory/view_inventory.html', {'inventory': inventory})
