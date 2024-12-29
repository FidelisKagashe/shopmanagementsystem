from django.contrib import admin
from .models import UserProfile, PasswordResetCode

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Display user email and username through the related User model
    list_display = ('user_email', 'user_username', 'phone_number')

    # Search through User's email, username, and phone number
    search_fields = ('user__email', 'user__username', 'phone_number') 

    # Filter by username from the related User model
    list_filter = ('user__username',)  

    # Prevent editing the email field from the related User model (readonly)
    readonly_fields = ('user_email',)  

    def has_add_permission(self, request):
        """Prevent adding new UserProfile objects from the admin."""
        return False

    def user_email(self, obj):
        """Custom method to access the user's email from the related User model."""
        return obj.user.email

    user_email.short_description = 'Email'  # Label for the 'user_email' field in the admin

    def user_username(self, obj):
        """Custom method to access the user's username from the related User model."""
        return obj.user.username

    user_username.short_description = 'Username'  # Label for the 'user_username' field in the admin


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    # Display all fields of the PasswordResetCode model
    list_display = (
        'user_email', 
        'reset_code', 
        'created_at', 
        'uidb64', 
        'token', 
        'expires_at', 
        'request_token'
    )

    # Search through User's email and reset code
    search_fields = ('user__email', 'reset_code')

    # Filter by username from the related User model
    list_filter = ('user__username',)

    # Prevent editing the email field from the related User model (readonly)
    readonly_fields = ('user_email', 'reset_code', 'created_at', 'uidb64', 'token', 'expires_at', 'request_token')

    # Custom method to retrieve user's email
    def user_email(self, obj):
        """Custom method to access the user's email from the related User model."""
        return obj.user.email

    user_email.short_description = 'Email'  # Label for the 'user_email' field in the admin