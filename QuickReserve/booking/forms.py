from django import forms
from .models import Room, Register_Employee, Room_Booking, Equipment
from django.contrib.auth.hashers import make_password

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'location', 'capacity', 'amenities']



class RegisterEmployeeForm(forms.ModelForm):
    emp_password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')

    class Meta:
        model = Register_Employee
        fields = ['emp_name', 'emp_gmail', 'emp_phoneNumber']  # Don't include password field from model

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("emp_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        employee = super().save(commit=False)
        # Set the password using Django's method
        employee.set_password(self.cleaned_data['emp_password'])  # ✅ correct!
        if commit:
            employee.save()
        return employee
    


class RoomBookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Room_Booking
        fields = ['room', 'meeting_title', 'participants', 'date', 'start_time', 'end_time', 'equipment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Dynamically load Equipment queryset
        self.fields['equipment'].queryset = Equipment.objects.all()
        self.fields['equipment'].widget = forms.CheckboxSelectMultiple()
        self.fields['equipment'].required = False
