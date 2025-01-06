from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

        return phone_number

    def save(self, commit=True):
        # Create the User object without saving yet
        user = super().save(commit=False)

        # Set the email from the form
        user.email = self.cleaned_data['email']

        if commit:
            # Save the user object to the database
            user.save()

            # Check if the user already has a UserProfile
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,  # Link the UserProfile to the User
                defaults={'phone_number': self.cleaned_data['phone_number']}  # Set phone number only if profile doesn't exist
            )

            # If the profile already exists, update the phone number
            if not created:
                user_profile.phone_number = self.cleaned_data['phone_number']
                user_profile.save()

        return user

        
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
