from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.events.models import Ticket
from .models import Booking
from .forms import BookingForm


@login_required
def booking_create(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, is_active=True)

    if not ticket.tickets_remaining:
        messages.error(request, "No tickets remaining for this type.")
        return redirect('events:event_detail', pk=ticket.event.pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, ticket=ticket)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.ticket = ticket
            try:
                booking.full_clean()  # Runs clean() validation
                booking.save()
                messages.success(request, f"Booking created! {booking.quantity} ticket(s) reserved.")
                # Later: redirect to payment initiation
                return redirect('events:event_detail', pk=ticket.event.pk)  # Temporary
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = BookingForm(ticket=ticket)

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'ticket': ticket,
        'event': ticket.event,
        'title': 'Book Tickets'
    })