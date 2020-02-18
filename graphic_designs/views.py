from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Post, Testimonial
from .forms import CheckoutForm
from users.models import Item, OrderItem, Order, BillingAddress

import stripe

stripe.api_key = settings.STRIPE_TEST_KEY

class HomeView(ListView):
    model = Item
    paginate_by = 3
    template_name = "app/home.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object':order
            }
            return render(self.request, "app/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:home")
        return render(self.request, "app/order_summary.html")

class ProductDetailView(DetailView):
    model = Item
    template_name = "app/product.html"

@login_required
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
            return redirect("core:order-summary")
        else:
            messages.success(request, "This item has been added to your cart")
            order.items.add(order_item)
            return redirect("core:order-summary")
    else: 
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item has been added to your cart")
    return redirect("core:order-summary")

@login_required
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
            return redirect("core:order-summary")
        else: 
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else: 
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else: 
                order.items.remove(order_item)
            messages.success(request, "This item quantity has been updated")
            return redirect("core:order-summary")
        else: 
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary", slug=slug)
    else: 
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "app/checkout_form.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                city = form.cleaned_data.get('city')
                country = form.cleaned_data.get('country')
                postcode = form.cleaned_data.get('postcode')
                # TODO: add functionality for these fields 
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    city=city,
                    postcode=postcode,
                    country=country,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                
                return redirect('core:checkout')
            messages.warning(self.request, "Checkout failed please check form for errors")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")

class PaymentView(View):
    def get(self, *args, **kwargs):
        # order 
        return render(self.request, "app/payment.html")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        stripe.Charge.create(
            amount=order.get_total() * 100, # to account for it being in pence
            currency="gbp",
            source=token
        )

        order.ordered = True
        