from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:ticket_id>/', views.booking_create, name='booking_create'),
    # Later: path('my-bookings/', views.my_bookings, name='my_bookings'),
]