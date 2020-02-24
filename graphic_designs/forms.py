from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('O', 'Other')
)

STAR_CHOICES = (
    ('0', 'Please leave a Rating'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField()
    city = forms.CharField()
    country = CountryField(blank_label="Select Country").formfield()
    postcode = forms.CharField()
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)

class ReviewForm(forms.Form):
    title = forms.CharField()
    review = forms.CharField(widget=forms.Textarea)
    star_rating = forms.ChoiceField(choices=STAR_CHOICES)