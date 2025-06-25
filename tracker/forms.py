from django import forms
from django.contrib.auth.models import User
from .models import *

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client_name', 'client_email', 'client_phone', 'client_address','billing_type', 'hourly_rate', 'fixed_rate']
   
    def clean(self):
        cleaned_data = super().clean()
        billing_type = cleaned_data.get("billing_type")

        if billing_type == 'hourly' and not cleaned_data.get("hourly_rate"):
            self.add_error("hourly_rate", "Hourly rate is required for hourly billing.")
        if billing_type == 'fixed' and not cleaned_data.get("fixed_rate"):
            self.add_error("fixed_rate", "Fixed rate is required for fixed billing.")
        
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    re_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_password")

        if password != re_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

class AccountUpdateForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New password and confirm password do not match.")
        return cleaned_data
    
class TimeEntryForm(forms.ModelForm):
    MODE_CHOICES = [
        ('manual', 'Enter hours manually'),
        ('timed', 'Use start and end time'),
        ('timer', 'Use live timer'),
    ]

    mode = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = TimeEntry
        fields = ['mode', 'start_time', 'end_time', 'manual_hours', 'description']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'manual_hours': forms.NumberInput(attrs={'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
        
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['due_date', 'notes', 'status']
        
class InvoiceStatusForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }