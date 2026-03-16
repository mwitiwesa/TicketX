from django import forms

class AttendeeNamesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quantity = kwargs.pop('quantity', 1)
        super().__init__(*args, **kwargs)
        for i in range(quantity):
            self.fields[f'name_{i}'] = forms.CharField(
                label=f'Attendee {i+1} Name',
                max_length=100,
                required=True,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )

    @property
    def names(self):
        return [self.cleaned_data[f'name_{i}'] for i in range(len(self.fields))]