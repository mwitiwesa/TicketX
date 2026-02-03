from django.shortcuts import render
from django.http import JsonResponse
from datetime import date
from .utils import get_calendar_data

def calendar_view(request):
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))

    data = get_calendar_data(year, month)
    return render(request, 'calendar_view/calendar.html', data)


def events_by_date(request):
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        day = int(request.GET.get('day'))
        selected_date = date(year, month, day)

        events = Event.objects.filter(
            is_active=True,
            event_date=selected_date
        ).order_by('event_time')

        html = render(request, 'calendar_view/day_events.html', {
            'events': events,
            'date': selected_date
        }).content.decode('utf-8')

        return JsonResponse({'html': html})
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid date'}, status=400)