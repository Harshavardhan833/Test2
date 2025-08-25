from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (FleetVehicle, Report,
                     TrailVehicle, Vehicle, VehicleChartData, VehicleRegistration,
                     VehicleSummary, VehicleType)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username')
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'fleet_owner'}
        }
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class FleetVehicleSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source='total_count')
    active = serializers.IntegerField(source='active_count')
    class Meta:
        model = FleetVehicle
        fields = ('title', 'value', 'active', 'special')

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('name', 'rating', 'speed', 'soc', 'range', 'temp', 'address')

class VehicleSummarySerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)
    fleet_name = serializers.CharField(source='fleet_type')
    summary_data = serializers.SerializerMethodField()
    class Meta:
        model = VehicleSummary
        fields = ('fleet_name', 'summary_data', 'vehicles')
    def get_summary_data(self, obj):
        return [
            {'title': 'Total Distance', 'value': str(obj.total_distance).split()[0], 'unit': 'km'},
            {'title': 'CO2 Savings', 'value': str(obj.co2_savings).split()[0], 'unit': 'kg'},
            {'title': 'Avg. Energy Consumption', 'value': str(obj.avg_energy_consumption).split()[0], 'unit': 'kWh'},
            {'title': 'Run Time', 'value': str(obj.run_time).split()[0], 'unit': 'hrs'},
            {'title': 'Traction Energy', 'value': str(obj.traction_energy).split()[0], 'unit': 'MWh'},
            {'title': 'Regen. Energy', 'value': str(obj.regen_energy).split()[0], 'unit': 'MWh'}
        ]

class VehicleChartDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleChartData
        fields = ('battery_data', 'temperature_data', 'voltage_data', 'current_data')

class VehicleRegistrationSerializer(serializers.ModelSerializer):
    dates = serializers.SerializerMethodField()
    class Meta:
        model = VehicleRegistration
        fields = ('id', 'registration_number', 'dates')
    def get_dates(self, obj):
        # PERFORMANCE NOTE: Ensure the view uses .prefetch_related('registrations__chart_data')
        return obj.chart_data.values_list('date', flat=True).order_by('-date')

class VehicleTypeSerializer(serializers.ModelSerializer):
    registrations = VehicleRegistrationSerializer(many=True, read_only=True)
    class Meta:
        model = VehicleType
        fields = ('id', 'name', 'registrations')

class TrailVehicleSerializer(serializers.ModelSerializer):
    available_dates = serializers.SerializerMethodField()
    class Meta:
        model = TrailVehicle
        fields = ('id', 'vehicle_type', 'registration_no', 'fleet', 'available_dates')
    def get_available_dates(self, obj):
        # PERFORMANCE NOTE: Ensure the view uses .prefetch_related('trail_data')
        return obj.trail_data.values_list('date', flat=True).distinct().order_by('-date')

class ReportSerializer(serializers.ModelSerializer):
    name = serializers.DateTimeField(format="%d %b %Y, %H:%M")
    registration_number = serializers.CharField(source='registration.registration_number', read_only=True)
    vehicle_type = serializers.CharField(source='registration.vehicle_type.name', read_only=True)

    class Meta:
        model = Report
        fields = (
            'id',  # <-- ADD THIS ID FIELD
            'name', 
            'vehicle_type', 
            'registration_number', 
            'report_type', 
            'col2', 
            'signal', 
            'signal0', 
            'signal1', 
            'signal2'
        )