from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'username', 'password1', 'password2')

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
