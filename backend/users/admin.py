from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import OfficerProfile

class OfficerProfileInline(admin.StackedInline):
    model = OfficerProfile
    can_delete = False
    verbose_name_plural = 'Officer Profile Information'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (OfficerProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(OfficerProfile)
class OfficerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'officer_id',
        'name',
        'designation',
        'department',
        'jurisdiction',
        'role',
        'is_active',
        'created_at'
    )
    list_filter = ('role', 'is_active', 'jurisdiction', 'department')
    search_fields = ('officer_id', 'name', 'user__username', 'jurisdiction')
    ordering = ('officer_id',)
    readonly_fields = ('created_at', 'updated_at')
