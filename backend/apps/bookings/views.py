from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Booking
from .forms import BookingForm
from apps.events.models import Ticket


@login_required
def booking_create(request, ticket_id):
    """
    View for selecting ticket quantity and creating a pending booking.
    Redirects to checkout page on success.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            # Check availability before saving
            if quantity > ticket.tickets_remaining:
                messages.error(request, f"Only {ticket.tickets_remaining} tickets remaining.")
                return render(request, 'bookings/booking_form.html', {
                    'form': form,
                    'ticket': ticket,
                    'event': event,
                })

            booking = form.save(commit=False)
            booking.user = request.user
            booking.ticket = ticket
            booking.total_price = ticket.price * quantity
            booking.status = 'PENDING'
            booking.save()

            messages.success(request, "Booking created successfully! Proceed to payment.")
            return redirect('bookings:checkout', booking_id=booking.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BookingForm(initial={'quantity': 1})

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'ticket': ticket,
        'event': event,
    })


@login_required
def checkout(request, booking_id):
    """
    Displays checkout page (GET) — payment initiation will be handled by Buni later.
    For now, shows placeholder message until Buni integration.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'PENDING':
        messages.error(request, "This booking cannot be paid anymore.")
        return redirect('events:event_detail', pk=booking.ticket.event.pk)

    if request.method == 'POST':
        # Placeholder: Buni integration will go here later
        messages.info(request, "Buni payment integration is coming soon. Booking reserved!")
        return redirect('bookings:checkout', booking_id=booking.id)

    return render(request, 'bookings/checkout.html', {
        'booking': booking,
        'ticket': booking.ticket,
        'event': booking.ticket.event,
    })


@login_required
def booking_detail(request, booking_id):
    """
    Optional: View to show booking status and download ticket if PAID.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'ticket': booking.ticket,
        'event': booking.ticket.event,
    })