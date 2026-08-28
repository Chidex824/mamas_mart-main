from django.shortcuts import render, get_object_or_404, redirect
from .models import Inventory, Category
from django.urls import reverse
from django.contrib import messages
from products.models import Purchase, Category as ProductCategory
from main.models import Supplier
from collections import defaultdict
from sales.models import Sale

def inventory_list(request):
    inventories = Inventory.objects.select_related('category').all()
    return render(request, 'inventory/inventory_list.html', {'inventories': inventories})

def add_inventory(request):
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        category_id = request.POST.get('category')
        supplier_name = request.POST.get('supplier')
        quantity = request.POST.get('quantity')
        location = request.POST.get('location')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        category = get_object_or_404(ProductCategory, id=category_id)

        inventory = Inventory.objects.create(
            item_name=item_name,
            category=category,
            supplier=supplier_name,
            quantity=quantity,
            location=location,
            price=price,
            description=description,
            image=image
        )
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
