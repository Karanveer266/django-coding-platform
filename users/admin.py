from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'date_joined', 'last_login',
        'problems_solved', 'current_streak', 'view_profile_link'  # Changed contest_rating to problems_solved
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 
        'last_login', 'preferred_language', 'theme_preference'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'view_profile_link']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('bio', 'location', 'website', 'avatar')
        }),
        ('Social Links', {
            'fields': ('github_username', 'linkedin_url')
        }),
        ('Coding Preferences', {
            'fields': ('preferred_language', 'theme_preference')
        }),
        ('Statistics', {
            'fields': ('current_streak', 'max_streak', 'total_submissions', 'accepted_submissions')
        }),
    )
    
    def view_profile_link(self, obj):
        if obj.pk:
            url = reverse('users:profile', args=[obj.username])
            return format_html('<a href="{}" target="_blank">View Profile</a>', url)
        return "N/A"
    view_profile_link.short_description = "Profile"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

# Customize admin site header
admin.site.site_header = "MyCodePlatform Administration"
admin.site.site_title = "MyCodePlatform Admin"
admin.site.index_title = "Welcome to MyCodePlatform Administration"