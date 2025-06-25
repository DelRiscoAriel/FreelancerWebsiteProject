from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta

from django.db import models

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Project(models.Model):
    BILLING_CHOICES = [
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Rate'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    billing_type = models.CharField(max_length=10, choices=BILLING_CHOICES, default='hourly')
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fixed_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(default=now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    manual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_running = models.BooleanField(default=False)

    def total_hours(self):
        if self.manual_hours:
            return self.manual_hours
        elif self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            hours = Decimal(duration.total_seconds() / 3600).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return hours
        return 0

    def __str__(self):
        return f"{self.project.name} - {self.total_hours()} hrs"

def get_future_date():
    return date.today() + timedelta(days=7)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Paid', 'Paid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(default=get_future_date)
    total_hours = models.DecimalField(max_digits=6, decimal_places=2,default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    def __str__(self):
        return f"Invoice #{self.id} for {self.project.name} ({self.status})"
