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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,  # Prevent ticket deletion if booked
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
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional: for time-limited reservations
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)  # For M-Pesa tracking

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __str__(self):
        return f"{self.user.email} - {self.quantity}x {self.ticket} ({self.status})"

    def clean(self):
        # Only basic validation here — no ticket access
        if self.quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")

    def save(self, *args, **kwargs):
        if self.pk is None:  # New booking
            self.total_price = self.ticket.price * self.quantity
            # Optional: set expires_at = now + 15 minutes
            # self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    @property
    def is_confirmed(self):
        return self.status == 'PAID'