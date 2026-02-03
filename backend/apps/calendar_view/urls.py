from django.urls import path
from . import views

app_name = 'calendar_view'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/', views.events_by_date, name='events_by_date'),
]