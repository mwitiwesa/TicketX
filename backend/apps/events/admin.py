from django.contrib import admin
from .models import Event, Ticket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_time', 'location', 'created_by', 'is_active')
    list_filter = ('is_active', 'event_date', 'created_by')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'event_date'
    readonly_fields = ('created_at', 'updated_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not change:  # New event
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1
    fields = ('name', 'price', 'quantity_available', 'is_active')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quantity_available', 'quantity_sold', 'tickets_remaining')
    list_filter = ('event', 'is_active')
    search_fields = ('name', 'event__title')