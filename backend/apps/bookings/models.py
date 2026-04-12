from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.events.models import Ticket


class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('USED', 'Used'),
    )

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
    expires_at = models.DateTimeField(null=True, blank=True)

    # Payment fields
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    # Attendee names
    attendee_names = models.JSONField(default=list, blank=True)

    # QR System Fields
    latest_qr_token = models.CharField(max_length=50, blank=True, null=True)
    scanned = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(null=True, blank=True)

    # Your existing fields
    is_used = models.BooleanField(default=False)         
    validated_at = models.DateTimeField(null=True, blank=True)
    scan_note = models.TextField(blank=True, null=True)

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
        if self.pk is None:
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

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='promo_codes')

    target_group = models.ForeignKey('auth.Group', null=True, blank=True, on_delete=models.SET_NULL)
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assigned_promos')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% - {self.event.title})"


class TicketScan(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='scans')
    ticket_index = models.PositiveIntegerField()
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Scanned By"
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('already_used', 'Already Used'),
        ('outdated', 'Outdated QR'),
        ('invalid', 'Invalid QR'),
    ], default='invalid')
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-scanned_at']
        verbose_name = "Ticket Scan Log"
        verbose_name_plural = "Ticket Scan Logs"

    def __str__(self):
        user_name = self.scanned_by.get_full_name() or self.scanned_by.email if self.scanned_by else "Unknown"
        return f"{user_name} scanned booking {self.booking.id} - {self.status}"