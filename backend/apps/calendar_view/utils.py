from datetime import date
from calendar import monthrange, month_name
from django.utils import timezone
from apps.events.models import Event


def get_calendar_data(year=None, month=None):
    """
    Returns calendar data for a given month.
    Returns a dict with:
    - year, month, month_name
    - calendar_days: flat list of dicts or None (padding)
    - prev/next month/year for navigation
    """
    today = timezone.now().date()
    year = year or today.year
    month = month or today.month

    try:
        first_weekday, days_in_month = monthrange(year, month)
    except ValueError:
        # Fallback if year/month invalid
        year = today.year
        month = today.month
        first_weekday, days_in_month = monthrange(year, month)

    # Unique event days in this month
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    event_dates = Event.objects.filter(
        is_active=True,
        event_date__range=[month_start, month_end]
    ).values_list('event_date', flat=True).distinct()

    event_days_set = {d.day for d in event_dates}

    # Flat list: padding + real days + end padding
    calendar_days = []

    # Padding before 1st
    for _ in range(first_weekday):
        calendar_days.append(None)

    # Real days
    for day_num in range(1, days_in_month + 1):
        calendar_days.append({
            'day': day_num,
            'has_event': day_num in event_days_set,
            'is_today': date(year, month, day_num) == today,
        })

    # Pad end to complete last week
    while len(calendar_days) % 7 != 0:
        calendar_days.append(None)

    return {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'calendar_days': calendar_days,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
    }