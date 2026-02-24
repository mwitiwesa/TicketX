from django.shortcuts import render
from django.db.models import Q
from apps.events.models import Event
from datetime import date, timedelta
from apps.calendar_view.utils import get_calendar_data


def home(request):
    today = date.today()

    # Get year and month from URL query params for calendar navigation
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    # Events today – always real today
    events_today = Event.objects.filter(
        is_active=True,
        event_date=today
    ).order_by('event_time')

    # Upcoming events – future events only (next 30 days, ordered by date)
    upcoming_events = Event.objects.filter(
        is_active=True,
        event_date__gt=today
    ).order_by('event_date', 'event_time')[:12]  # show up to 12 for carousel

    # Calendar data (based on URL year/month)
    calendar_data = get_calendar_data(year=year, month=month)

    context = {
        'events_today': events_today,
        'upcoming_events': upcoming_events,
        'today': today,
        'calendar_days': calendar_data['calendar_days'],
        'year': calendar_data['year'],
        'month': calendar_data['month'],
        'month_name': calendar_data['month_name'],
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