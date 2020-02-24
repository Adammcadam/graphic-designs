from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Review
from .forms import CheckoutForm, ReviewForm
from users.models import Item, OrderItem, Order, BillingAddress, Payment

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

def product(request, slug):
    item = get_object_or_404(Item, slug=slug)
    review = Review.objects.all()
    form = ReviewForm()
    context = {
        'form': form,
        'item': item,
        'review': review
    }
    return render(request, "app/product.html", context)

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
                
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'O':
                    return redirect('core:payment', payment_option='other')
                else:
                    messages.warning(self.request, "Invalid payment option")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order':order
        }
        return render(self.request, "app/payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = order.get_total() * 100, # to account for it being in pence

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="gbp",
                source=token
            )

            # create the payment 
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order 

            order.ordered = True
            order.payment = payment
            order.save()

            # TODO: add a order confirmation page 
            messages.success(self.request, "Your order was successful, now sit back and relax")
            return redirect('core:home')
        except stripe.error.CardError as e:
            body = e.json_body
            error = body.get('error',{})
            messages.warning(self.request, f"{error.get('message')}")
            return redirect('core:home')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Too many requests")
            return redirect('core:home')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parameters")
            return redirect('core:home')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect('core:home')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Unable to connect to stripe")
            return redirect('core:home')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, "Something went wrong, you have not been charged. Please try again")
            return redirect('core:home')
        except Exception as e:
            # send email to self 
            messages.warning(self.request, "Serious error has occured we have been notified")
            return redirect('core:home')

        