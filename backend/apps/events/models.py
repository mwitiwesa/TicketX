from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to='events/images/',
        blank=True,
        null=True,
        help_text="Event poster or main image"
    )
    location = models.CharField(max_length=200, blank=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ADMIN'},
        related_name='created_events'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-event_date', '-event_time']
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return f"{self.title} ({self.event_date})"

    @property
    def has_tickets(self):
        return self.tickets.exists()


class Ticket(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    name = models.CharField(max_length=100, help_text="e.g. Regular, VIP, Student")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField(default=100)
    quantity_sold = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']
        unique_together = ['event', 'name']  # Prevent duplicate ticket types per event

    def __str__(self):
        return f"{self.name} - {self.event.title} (KES {self.price})"

    @property
    def tickets_remaining(self):
        return self.quantity_available - self.quantity_sold