from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
  
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('fleet_owner', 'Fleet Owner'),
        ('sales', 'Sales'),
        ('service', 'Service'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='fleet_owner')
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

class FleetVehicle(models.Model):
    """Stores the summary data for each type of fleet vehicle."""
    title = models.CharField(max_length=100, unique=True)
    total_count = models.PositiveIntegerField(default=0)
    active_count = models.PositiveIntegerField(default=0)
    special = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order on the dashboard")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class PerformanceStat(models.Model):
    """Stores a single key-value performance metric for the dashboard."""
    key = models.CharField(max_length=100, unique=True, primary_key=True, help_text="A unique key for the stat, e.g., 'total_distance'")
    title = models.CharField(max_length=100, help_text="The human-readable title, e.g., 'Total Distance'")
    value = models.CharField(max_length=100, help_text="The value with units, e.g., '12,500 km'")
    order = models.PositiveIntegerField(default=0, help_text="The display order on the dashboard")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
class VehicleSummary(models.Model):
    fleet_type = models.CharField(max_length=100, unique=True); total_distance = models.CharField(max_length=50); co2_savings = models.CharField(max_length=50); avg_energy_consumption = models.CharField(max_length=50); run_time = models.CharField(max_length=50); traction_energy = models.CharField(max_length=50); regen_energy = models.CharField(max_length=50)
class Vehicle(models.Model):
    summary = models.ForeignKey(VehicleSummary, related_name='vehicles', on_delete=models.CASCADE); name = models.CharField(max_length=100); rating = models.CharField(max_length=10); speed = models.IntegerField(); soc = models.IntegerField(); range = models.IntegerField(); temp = models.IntegerField(); address = models.CharField(max_length=255)
class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
class VehicleRegistration(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, related_name='registrations', on_delete=models.CASCADE); registration_number = models.CharField(max_length=100, unique=True)
class VehicleChartData(models.Model):
    registration = models.ForeignKey(VehicleRegistration, related_name='chart_data', on_delete=models.CASCADE); date = models.DateField(); battery_data = models.JSONField(default=dict); temperature_data = models.JSONField(default=dict); voltage_data = models.JSONField(default=dict); current_data = models.JSONField(default=dict)
    class Meta: unique_together = ('registration', 'date')
class TrailVehicle(models.Model):
    vehicle_type = models.CharField(max_length=100); registration_no = models.CharField(max_length=100, unique=True); fleet = models.CharField(max_length=100)
class TrailDataPoint(models.Model):
    vehicle = models.ForeignKey(TrailVehicle, related_name='trail_data', on_delete=models.CASCADE); date = models.DateField(); metrics = models.JSONField(default=dict); ecu_data = models.JSONField(default=dict); coordinates = models.JSONField(default=dict)
    class Meta: ordering = ['date']
class Report(models.Model):
    registration = models.ForeignKey(VehicleRegistration, related_name='reports', on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    name = models.DateTimeField()
    col2 = models.CharField(max_length=50)
    signal = models.CharField(max_length=50)
    signal0 = models.CharField(max_length=50)
    signal1 = models.CharField(max_length=50)
    signal2 = models.CharField(max_length=50)
    class Meta: ordering = ['-name']
    def __str__(self): return f"Report for {self.registration.registration_number} at {self.name}"