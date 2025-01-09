from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

#Added
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

#Added
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


#End


class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'username', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number').strip()

        # Check if the phone number starts with '+255' and is 13 characters long
        if not phone_number.startswith('+255'):
            raise ValidationError("Phone number must start with +255.")
        
        if len(phone_number) != 13:
            raise ValidationError("Phone number must be exactly 13 digits long.")
        
        # Check if the phone number contains only digits and the '+' sign
        if not all(c.isdigit() or c == '+' for c in phone_number):
            raise ValidationError("Phone number must only contain digits and the '+' sign.")

        # Ensure phone number is unique
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already associated with another account.")

        return phone_number
    
    
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# UserForm for basic user info
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'readonly': 'readonly',
                'class': 'mt-1 p-2 border border-gray-300 rounded w-full bg-gray-100 text-gray-500',
            }),
            'username': forms.TextInput(attrs={
                'class': 'mt-1 p-2 border border-gray-300 rounded w-full',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 p-2 border border-gray-300 rounded w-full',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 p-2 border border-gray-300 rounded w-full',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if the username is already taken
        if username and User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username


# UserProfileForm for phone number
class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 p-2 border border-gray-300 rounded w-full',
            'placeholder': 'Enter phone number',
        })
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Check if the phone number exists for another user
            user_profile = UserProfile.objects.filter(phone_number=phone_number).exclude(user=self.instance.user).first()
            if user_profile:
                raise ValidationError("This phone number is already in use. Please provide a unique number.")
        return phone_number
