from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
    ('O', 'Other')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField()
    city = forms.CharField()
    country = CountryField(blank_label="Select Country")
    postcode = forms.CharField()
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput())
    save_info = forms.BooleanField(widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)