from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobListing, Log
from .models import Resume


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'email_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('role', 'email_verified', 'verification_token')}),  # Add your fields here
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'email_verified'),
        }),
    )


# Register JobListing Model
@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter')
    search_fields = ('title', 'recruiter__username')
    list_filter = ('recruiter',)


# Register Log Model
@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'action', 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)
