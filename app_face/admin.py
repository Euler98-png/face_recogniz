from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AdminUser, UserProfile

# Enregistrer AdminUser
class AdminUserAdmin(UserAdmin):
    model = AdminUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']
    ordering = ['username']

# Enregistrer UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'function', 'email', 'phone', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email']

admin.site.register(AdminUser, AdminUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
