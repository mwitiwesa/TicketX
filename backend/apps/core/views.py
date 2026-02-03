from django.shortcuts import render
from django.db.models import Q
from apps.events.models import Event
from datetime import date, timedelta
from apps.calendar_view.utils import get_calendar_data


def home(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    events_today = Event.objects.filter(
        is_active=True,
        event_date=today
    ).order_by('event_time')

    upcoming = Event.objects.filter(
        is_active=True,
        event_date__gte=tomorrow,
        event_date__lte=today + timedelta(days=7)
    ).order_by('event_date', 'event_time')

    # Get calendar data
    calendar_data = get_calendar_data()

    context = {
        'events_today': events_today,
        'upcoming': upcoming,
        'today': today,
        'calendar_days': calendar_data['calendar_days'],
        'year': calendar_data['year'],
        'month': calendar_data['month'],
        'month_name': calendar_data['month_name'],
        # Optional navigation
        'prev_month': calendar_data['prev_month'],
        'prev_year': calendar_data['prev_year'],
        'next_month': calendar_data['next_month'],
        'next_year': calendar_data['next_year'],
    }
    return render(request, 'core/home.html', context)

def search(request):
    query = request.GET.get('q', '').strip()
    results = Event.objects.none()

    if query:
        results = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        ).filter(is_active=True).order_by('event_date')

    return render(request, 'core/search_results.html', {
        'results': results,
        'query': query
    })