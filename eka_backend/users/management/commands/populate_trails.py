import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from users.models import TrailVehicle, TrailDataPoint

class Command(BaseCommand):
    help = 'Populates the database with initial data for the Trails page.'

    def handle(self, *args, **options):
        self.stdout.write('Populating Trails data...')
        TrailVehicle.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing trails data.'))

        # --- Create Trail Vehicles ---
        v1 = TrailVehicle.objects.create(vehicle_type='EKA 9', registration_no='MH 14 AB 1234', fleet='PMPML')
        v2 = TrailVehicle.objects.create(vehicle_type='EKA 7', registration_no='MH 01 CD 5678', fleet='BEST')
        v3 = TrailVehicle.objects.create(vehicle_type='EKA 7', registration_no='MH 01 CD 5679', fleet='BEST')
        self.stdout.write(self.style.SUCCESS('Created trail vehicles.'))

        # --- Create Trail Data for Vehicle 1 on two different dates ---
        # Base metrics and ECU data
        base_metrics_v1 = {'speed': {'value': '62', 'unit': 'kmph'}, 'soc': {'value': '88', 'unit': '%'}, 'motorSpeed': {'value': '1800', 'unit': 'rpm'}, 'motorTorque': {'value': '190', 'unit': 'nm'}, 'acceleration': {'value': '3.1', 'unit': 'km/s²'}, 'brake': {'value': '0', 'unit': '%'}, 'faults': {'value': 'None', 'unit': ''}}
        base_ecu_v1 = [{'name': 'BMS', 'controls': [{'name': 'Contactor Control', 'value': '1'}, {'name': 'Enable', 'value': '1'}]}, {'name': 'Motor', 'controls': [{'name': 'Torque Command (Nm)', 'value': '1500'}, {'name': 'Enable', 'value': '1'}]}]
        
        # Trail path (a simple loop)
        start_lat, start_lng = 18.5204, 73.8567
        path_v1 = [(start_lat + i * 0.001, start_lng + i * 0.001) for i in range(5)] + \
                  [(start_lat + 0.005, start_lng + 0.005 - i * 0.001) for i in range(5)]
        
        for d in range(2): # Create data for today and yesterday
            current_date = date.today() - timedelta(days=d)
            for lat, lng in path_v1:
                TrailDataPoint.objects.create(
                    vehicle=v1, date=current_date, metrics=base_metrics_v1, ecu_data=base_ecu_v1,
                    coordinates={'lat': lat, 'lng': lng}
                )
        self.stdout.write(self.style.SUCCESS(f'Created trail for {v1.registration_no} on 2 dates.'))

        # --- Create Trail Data for Vehicle 2 ---
        base_metrics_v2 = {'speed': {'value': '45', 'unit': 'kmph'}, 'soc': {'value': '95', 'unit': '%' }, 'motorSpeed': {'value': '1550', 'unit': 'rpm'}, 'motorTorque': {'value': '165', 'unit': 'nm'}, 'acceleration': {'value': '0', 'unit': 'km/s²'}, 'brake': {'value': '10', 'unit': '%'}, 'faults': {'value': 'Minor', 'unit': ''}}
        base_ecu_v2 = [{'name': 'BMS', 'controls': [{'name': 'Contactor Control', 'value': '2'}, {'name': 'Enable', 'value': '0'}]}, {'name': 'HVPDU', 'controls': [{'name': 'Contactor Control', 'value': '3'}, {'name': 'Enable', 'value': '1'}]}]
        path_v2 = [(start_lat - i * 0.001, start_lng + i * 0.001) for i in range(8)]
        for lat, lng in path_v2:
            TrailDataPoint.objects.create(
                vehicle=v2, date=date.today(), metrics=base_metrics_v2, ecu_data=base_ecu_v2,
                coordinates={'lat': lat, 'lng': lng}
            )
        self.stdout.write(self.style.SUCCESS(f'Created trail for {v2.registration_no}.'))
