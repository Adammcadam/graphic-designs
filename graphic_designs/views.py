from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Post, Testimonial
from users.models import Item, OrderItem, Order

class HomeView(ListView):
    model = Item
    paginate_by = 3
    template_name = "app/home.html"

class ProductDetailView(DetailView):
    model = Item
    template_name = "app/product.html"

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # ensure we aren't getting an item that has already been ordered
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    # check if item is not already ordered 
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        # check if order item is in the order 
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, "This item has been updated in your cart")
        else:
            messages.success(request, "This item has been added to your cart")
            order.items.add(order_item)
    else: 
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item has been added to your cart")
    return redirect("core:product", slug=slug)

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if item is not already ordered 
    order_query = Order.objects.filter(user=request.user, ordered=False)
    if order_query.exists():
        order = order_query[0]
        # check if order item is in the order 
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.success(request, "This item has been removed from your cart")
        else: 
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else: 
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)
