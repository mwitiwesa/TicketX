from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.events.models import Ticket


class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    )
    is_used = models.BooleanField(default=False)         
    validated_at = models.DateTimeField(null=True, blank=True)
    scan_note = models.TextField(blank=True, null=True)


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional: reservation expiry

    # Payment fields
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)  # e.g. Buni txn ID

    # Attendee names for multi-ticket bookings
    attendee_names = models.JSONField(default=list, blank=True)  # ["John Doe", "Jane Smith", ...]

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __str__(self):
        return f"{self.user.email} - {self.quantity}x {self.ticket} ({self.status})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")

    def save(self, *args, **kwargs):
        if self.pk is None:  # New booking
            self.total_price = self.ticket.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def is_confirmed(self):
        return self.status == 'PAID' and self.is_paid

    @property
    def attendee_count(self):
        return len(self.attendee_names) if self.attendee_names else self.quantity
    
class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    # NEW: Link to specific event (required for your feature)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='promo_codes')

    # Optional: Assign to group (e.g. "Bidco Influencer", "Sponsors")
    target_group = models.ForeignKey('auth.Group', null=True, blank=True, on_delete=models.SET_NULL)

    # Optional: Assign to specific users (influencers)
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assigned_promos')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% - {self.event.title})"