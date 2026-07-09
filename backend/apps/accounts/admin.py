from django.contrib import admin

from .models import StaffMembership, Store, UserProfile


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "city", "state", "created_at")
    search_fields = ("name", "owner__email", "city", "state")


@admin.register(StaffMembership)
class StaffMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "store", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "store__name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "default_store", "timezone")
