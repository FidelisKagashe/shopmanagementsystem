from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory
from .models import SaleOrder, SaleOrderItem, UserFinancialTransaction
from decimal import Decimal


class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Avoid user enumeration: don't reveal whether the email is correct
        users = User.objects.filter(email=email)

        # If multiple users are found, choose the first one (or handle as needed)
        if users.count() == 1:
            user = users.first()
        else:
            user = None

        if user:
            # Authenticate using the email and password
            user = authenticate(username=user.username, password=password)

        if user is None:
            # Return a generic error message for both wrong email and password
            raise forms.ValidationError("Invalid email or password.")

        self.cleaned_data['username'] = user.username

        return self.cleaned_data


class SaleOrderForm(forms.ModelForm):
    class Meta:
        model = SaleOrder
        fields = ['customer', 'created_by', 'status', 'payment_status']
        # order_date and total_amount are automatically handled

    def __init__(self, *args, **kwargs):
        super(SaleOrderForm, self).__init__(*args, **kwargs)
        # Make all SaleOrderForm fields required
        for field_name, field in self.fields.items():
            field.required = True
            # Add a common CSS class for styling; your CSS can then style errors in red.
            field.widget.attrs.update({'class': 'form-control'})

class SaleOrderItemForm(forms.ModelForm):
    class Meta:
        model = SaleOrderItem
        fields = ['product', 'quantity', 'sale_price', 'discount']
        widgets = {
            # Pre-fill sale_price (from product unit_price) and keep it read-only in the form.
            'sale_price': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SaleOrderItemForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Make all fields required except for 'discount'
            if field_name != 'discount':
                field.required = True
            else:
                field.required = False
                # Set default initial value for discount
                field.initial = Decimal('0.00')
            # Add a common CSS class for styling
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})

SaleOrderItemFormSet = inlineformset_factory(
    SaleOrder,
    SaleOrderItem,
    form=SaleOrderItemForm,
    extra=1,
    can_delete=True
)


class UserFinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = UserFinancialTransaction
        fields = ['description', 'amount', 'transaction_type', 'account', 'approved']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
            'account': forms.Select(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
            'approved': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
        labels = {
            'approved': 'Approved',
        }