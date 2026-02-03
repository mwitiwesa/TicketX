from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'ticket__event')
    search_fields = ('user__email', 'ticket__event__title', 'ticket__name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        # Optional: prevent manual creation in admin (better via frontend)
        return False  # or True if you want admins to create manually