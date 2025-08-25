import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from users.models import (
    FleetVehicle, PerformanceStat, VehicleSummary, Vehicle,
    VehicleType, VehicleRegistration, VehicleChartData,
    TrailVehicle, TrailDataPoint, Report
)

class Command(BaseCommand):
    help = 'Populates the database with a complete set of initial data for all app features.'

    def _generate_chart_data(self, config):
        """Helper function to generate random chart data."""
        labels = [f"{h:02d}:{(m*15):02d}" for h in range(8, 18) for m in range(4)]
        series = [
            {
                'name': y_axis['name'],
                'data': [round(random.uniform(y_axis['min'], y_axis['max']), 2) for _ in labels]
            } for y_axis in config['y_axes']
        ]
        return {'labels': labels, 'series': series}

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Full Database Seed ---'))

        # Clear old data in the correct order to respect dependencies
        self._clear_data()

        # Create data in the correct order
        self._create_dashboard_data()
        self._create_vehicle_selection_data()
        registrations = self._create_vehicle_analysis_data()
        self._create_trails_data()
        self._create_reports_data(registrations)

        self.stdout.write(self.style.SUCCESS('--- Finished Full Database Seed ---'))

    def _clear_data(self):
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        # Delete in reverse order of creation to avoid foreign key constraints
        Report.objects.all().delete()
        TrailDataPoint.objects.all().delete()
        TrailVehicle.objects.all().delete()
        VehicleChartData.objects.all().delete()
        VehicleRegistration.objects.all().delete()
        VehicleType.objects.all().delete()
        Vehicle.objects.all().delete()
        VehicleSummary.objects.all().delete()
        PerformanceStat.objects.all().delete()
        FleetVehicle.objects.all().delete()
        self.stdout.write('Existing data cleared.')

    def _create_dashboard_data(self):
        self.stdout.write('Populating Dashboard data (Fleet & Performance)...')
        fleet_data = [
            {'title': 'EKA 7', 'total_count': 12, 'active_count': 8, 'special': True},
            {'title': 'EKA 9', 'total_count': 8, 'active_count': 6, 'special': False},
            {'title': 'EKA 12', 'total_count': 5, 'active_count': 5, 'special': False},
        ]
        FleetVehicle.objects.bulk_create([FleetVehicle(**data) for data in fleet_data])

        performance_data = [
            {'key': 'total_distance', 'title': 'Total Distance', 'value': '12,500 km'},
            {'key': 'co2_savings', 'title': 'CO2 Savings', 'value': '1.2 tons'},
            {'key': 'avg_energy_consumption', 'title': 'Avg. Energy Consumption', 'value': '0.8 kWh/km'},
        ]
        PerformanceStat.objects.bulk_create([PerformanceStat(**data) for data in performance_data])
        self.stdout.write(self.style.SUCCESS('Dashboard data created.'))

    def _create_vehicle_selection_data(self):
        self.stdout.write('Populating Vehicle Selection data...')
        summary = VehicleSummary.objects.create(
            fleet_type='Eka 7', total_distance='1280 km', co2_savings='150 kg',
            avg_energy_consumption='0.9 kWh', run_time='45 hrs',
            traction_energy='1.1 MWh', regen_energy='0.2 MWh'
        )
        vehicles_data = [
            {'summary': summary, 'name': 'MH12 AB 1234', 'rating': '4.8', 'speed': 25, 'soc': 78, 'range': 90, 'temp': 32, 'address': 'Near Balewadi High Street, Pune'},
            {'summary': summary, 'name': 'MH14 CD 5678', 'rating': '4.5', 'speed': 0, 'soc': 92, 'range': 110, 'temp': 28, 'address': 'Parked at Baner, Pune'},
            {'summary': summary, 'name': 'MH01 EF 9101', 'rating': '4.9', 'speed': 40, 'soc': 65, 'range': 75, 'temp': 35, 'address': 'Enroute Hinjewadi Phase 3, Pune'},
        ]
        Vehicle.objects.bulk_create([Vehicle(**data) for data in vehicles_data])
        self.stdout.write(self.style.SUCCESS('Vehicle Selection data created.'))

    def _create_vehicle_analysis_data(self):
        self.stdout.write('Populating Vehicle Analysis data...')
        eka7 = VehicleType.objects.create(name='Eka 7')
        reg1 = VehicleRegistration.objects.create(vehicle_type=eka7, registration_number='MH12 AB 1234')
        reg2 = VehicleRegistration.objects.create(vehicle_type=eka7, registration_number='MH14 CD 5678')
        
        eka9 = VehicleType.objects.create(name='Eka 9')
        reg3 = VehicleRegistration.objects.create(vehicle_type=eka9, registration_number='MH01 EF 9101')
        
        today = date.today()
        charts_to_create = []
        for reg in [reg1, reg2, reg3]:
            for i in range(2): # Data for 2 days
                charts_to_create.append(VehicleChartData(
                    registration=reg, date=today - timedelta(days=i),
                    battery_data=self._generate_chart_data({'y_axes': [{'name': 'Voltage', 'min': 20, 'max': 28}]}),
                    temperature_data=self._generate_chart_data({'y_axes': [{'name': 'Min Temp', 'min': 20, 'max': 32}, {'name': 'Max Temp', 'min': 22, 'max': 36}]}),
                    
                    # --- ADD THESE TWO MISSING LINES ---
                    voltage_data=self._generate_chart_data({'y_axes': [{'name': 'A Pack', 'min': 680, 'max': 705}, {'name': 'B Pack', 'min': 685, 'max': 710}]}),
                    current_data=self._generate_chart_data({'y_axes': [{'name': 'Current', 'min': 670, 'max': 695}, {'name': 'Peak', 'min': 690, 'max': 700}]})
                ))
        VehicleChartData.objects.bulk_create(charts_to_create)
        self.stdout.write(self.style.SUCCESS('Vehicle Analysis data created.'))
        return [reg1, reg2, reg3]

    def _create_trails_data(self):
        self.stdout.write('Populating Trails data...')
        v1 = TrailVehicle.objects.create(vehicle_type='EKA 9', registration_no='MH 14 AB 1234', fleet='PMPML')
        v2 = TrailVehicle.objects.create(vehicle_type='EKA 7', registration_no='MH 01 CD 5678', fleet='BEST')
        
        points_to_create = []
        start_lat, start_lng = 18.6421, 73.7861 # Near Nanekarwadi, Pune
        path = [(start_lat + i * 0.001, start_lng + i * 0.001) for i in range(8)]

        for v in [v1, v2]:
             for i in range(2): # Data for 2 days
                for lat, lng in path:
                    points_to_create.append(TrailDataPoint(
                        vehicle=v, date=date.today() - timedelta(days=i),
                        metrics={'speed': {'value': random.randint(40, 60), 'unit': 'kmph'}, 'soc': {'value': random.randint(70, 95), 'unit': '%'}},
                        ecu_data=[{'name': 'BMS', 'controls': [{'name': 'Enable', 'value': '1'}]}],
                        coordinates={'lat': lat, 'lng': lng}
                    ))
        TrailDataPoint.objects.bulk_create(points_to_create)
        self.stdout.write(self.style.SUCCESS('Trails data created.'))

    def _create_reports_data(self, registrations):
        self.stdout.write('Populating Reports data...')
        report_types = ['Performance', 'Health', 'Charging', 'Fault']
        reports_to_create = [
            Report(
                registration=random.choice(registrations),
                report_type=random.choice(report_types),
                name=timezone.now() - timedelta(days=random.randint(0, 30)),
                col2=f"Val-{random.randint(10, 99)}",
                signal=f"Sig-{random.randint(100, 999)}",
                signal0=f"S0-{random.randint(0,1)}",
                signal1=f"S1-{random.randint(0,1)}",
                signal2=f"S2-{random.randint(0,1)}"
            ) for _ in range(200) # Create 200 reports
        ]
        Report.objects.bulk_create(reports_to_create)
        self.stdout.write(self.style.SUCCESS('Reports data created.'))