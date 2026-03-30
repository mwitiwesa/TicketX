from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:ticket_id>/', views.booking_create, name='booking_create'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:booking_id>/download/', views.download_tickets, name='download_tickets'),
    #path('booking/<int:booking_id>/names/', views.add_attendee_names, name='add_attendee_names'),
    path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('validate-qr/', views.validate_qr, name='validate_qr'),
    #path('ticket-action/<int:booking_id>/', views.ticket_action, name='ticket_action'),
    path('generate-promo/<int:event_id>/', views.generate_promo_code, name='generate_promo_code'),
]