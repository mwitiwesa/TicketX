from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'ticket',
        'quantity',
        'total_price',
        'status',
        'is_paid',
        'created_at',
    )
    list_filter = ('status', 'is_paid', 'created_at', 'ticket__event')
    search_fields = ('user__email', 'ticket__event__title', 'ticket__name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    # Prevent manual creation in admin (recommended — use frontend instead)
    def has_add_permission(self, request):
        return False  # change to True if admins should create bookings manually

    # Add QR Scanner link/button in the admin change list (Bookings list page)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['qr_scanner_url'] = reverse('bookings:qr_scanner')
        return super().changelist_view(request, extra_context=extra_context)

    # Optional: custom admin URLs (not strictly needed if using direct URL)
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('qr-scanner/', self.admin_site.admin_view(self.qr_scanner_redirect), name='bookings_qr_scanner'),
        ]
        return custom_urls + urls

    def qr_scanner_redirect(self, request):
        """Admin redirect to the main scanner view"""
        return redirect(reverse('bookings:qr_scanner'))

    # Optional: Add a nice link in the admin header or object tools
    def get_object_tools(self, request, extra_context=None):
        tools = super().get_object_tools(request, extra_context)
        tools.append(format_html(
            '<a href="{}" class="button" style="background:#4caf50; color:white;" target="_blank">'
            'Open QR Ticket Scanner</a>',
            reverse('bookings:qr_scanner')
        ))
        return tools