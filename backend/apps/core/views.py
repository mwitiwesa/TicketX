from django.shortcuts import render
from django.db.models import Q
from apps.events.models import Event
from datetime import date, timedelta
from apps.calendar_view.utils import get_calendar_data


def home(request):
    today = date.today()

    # Get year and month from URL query params (for navigation), default to current month
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    # Events Today – always use real today (not affected by calendar navigation)
    events_today = Event.objects.filter(
        is_active=True,
        event_date=today
    ).order_by('event_time')

    # Upcoming – future events from real today (30 days ahead)
    upcoming = Event.objects.filter(
        is_active=True,
        event_date__gt=today,
        event_date__lte=today + timedelta(days=30)
    ).order_by('event_date', 'event_time')

    # Calendar data – use the year/month from URL params
    calendar_data = get_calendar_data(year=year, month=month)

    # Debug prints – keep these to verify
    print("DEBUG: URL params year/month:", year, month)
    print("DEBUG: Calendar displaying:", calendar_data['month_name'], calendar_data['year'])
    print("DEBUG: Events today count:", events_today.count())
    print("DEBUG: Upcoming count:", upcoming.count())
    print("DEBUG: Red days in displayed month:", 
          {ev.event_date.day for ev in Event.objects.filter(
              is_active=True,
              event_date__month=calendar_data['month'],
              event_date__year=calendar_data['year']
          )})

    context = {
        'events_today': events_today,
        'upcoming': upcoming,
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