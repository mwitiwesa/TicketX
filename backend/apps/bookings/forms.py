from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)
        if self.ticket:
            self.fields['quantity'].widget.attrs['max'] = self.ticket.tickets_remaining