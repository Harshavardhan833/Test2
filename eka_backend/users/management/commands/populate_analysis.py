import random
from datetime import date
from django.core.management.base import BaseCommand
from users.models import VehicleType, VehicleRegistration, VehicleChartData

class Command(BaseCommand):
    help = 'Populates the database with initial data for the Vehicle Analysis page.'

    def handle(self, *args, **options):
        self.stdout.write('Populating Vehicle Analysis data...')

        # --- Helper function to generate chart data ---
        def generate_chart_data(config):
            labels = [f"{h:02d}:{(m*15):02d}" for h in range(8, 18) for m in range(4)]
            series = [{'name': y['name'], 'data': [round(random.uniform(y['min'], y['max']), 2) for _ in labels]} for y in config['y_axes']]
            return {'labels': labels, 'series': series}

        # --- Clear existing data to avoid duplicates ---
        VehicleType.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing analysis data.'))

        # --- Create Vehicle Types and Registrations ---
        eka7 = VehicleType.objects.create(name='Eka 7')
        reg1 = VehicleRegistration.objects.create(vehicle_type=eka7, registration_number='MH12 AB 1234')
        reg2 = VehicleRegistration.objects.create(vehicle_type=eka7, registration_number='MH14 CD 5678')
        
        eka9 = VehicleType.objects.create(name='Eka 9')
        reg3 = VehicleRegistration.objects.create(vehicle_type=eka9, registration_number='MH01 EF 9101')

        self.stdout.write(self.style.SUCCESS('Created vehicle types and registrations.'))

        # --- Create Chart Data for specific dates ---
        VehicleChartData.objects.create(
            registration=reg1, date=date(2025, 8, 11),
            battery_data=generate_chart_data({'y_axes': [{'name': 'Voltage', 'min': 20, 'max': 28}]}),
            temperature_data=generate_chart_data({'y_axes': [{'name': 'Min Temp', 'min': 20, 'max': 32}, {'name': 'Max Temp', 'min': 22, 'max': 36}]}),
            voltage_data=generate_chart_data({'y_axes': [{'name': 'A Pack', 'min': 680, 'max': 705}, {'name': 'B Pack', 'min': 685, 'max': 710}]}),
            current_data=generate_chart_data({'y_axes': [{'name': 'Current', 'min': 670, 'max': 695}, {'name': 'Peak', 'min': 690, 'max': 700}]})
        )
        VehicleChartData.objects.create(
            registration=reg1, date=date(2025, 8, 12),
            battery_data=generate_chart_data({'y_axes': [{'name': 'Voltage', 'min': 22, 'max': 27}]}),
            temperature_data=generate_chart_data({'y_axes': [{'name': 'Min Temp', 'min': 25, 'max': 35}, {'name': 'Max Temp', 'min': 28, 'max': 38}]}),
            voltage_data=generate_chart_data({'y_axes': [{'name': 'A Pack', 'min': 682, 'max': 702}, {'name': 'B Pack', 'min': 688, 'max': 712}]}),
            current_data=generate_chart_data({'y_axes': [{'name': 'Current', 'min': 675, 'max': 698}, {'name': 'Peak', 'min': 692, 'max': 701}]})
        )
        VehicleChartData.objects.create(
            registration=reg3, date=date(2025, 8, 12),
            battery_data=generate_chart_data({'y_axes': [{'name': 'Voltage', 'min': 18, 'max': 25}]}),
            temperature_data=generate_chart_data({'y_axes': [{'name': 'Min Temp', 'min': 18, 'max': 28}, {'name': 'Max Temp', 'min': 20, 'max': 30}]}),
            voltage_data=generate_chart_data({'y_axes': [{'name': 'A Pack', 'min': 670, 'max': 690}, {'name': 'B Pack', 'min': 675, 'max': 695}]}),
            current_data=generate_chart_data({'y_axes': [{'name': 'Current', 'min': 660, 'max': 680}, {'name': 'Peak', 'min': 670, 'max': 685}]})
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated chart data.'))
