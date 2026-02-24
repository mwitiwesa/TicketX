from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:ticket_id>/', views.booking_create, name='booking_create'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
]