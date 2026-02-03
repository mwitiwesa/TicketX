from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Ticket
from .forms import EventForm


@login_required
def event_create(request):
    if not request.user.is_admin:
        messages.error(request, "Only admins can create events.")
        return redirect('core:home')  # We'll create core later

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})


def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('event_date')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    tickets = event.tickets.filter(is_active=True)
    return render(request, 'events/event_detail.html', {'event': event, 'tickets': tickets})