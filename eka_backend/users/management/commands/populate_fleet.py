from django.core.management.base import BaseCommand
from users.models import FleetVehicle, PerformanceStat # Import both models

class Command(BaseCommand):
    help = 'Populates the database with initial fleet and performance data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Initial Data Population ---'))
        
        self._populate_fleet()
        self._populate_performance()
        
        self.stdout.write(self.style.SUCCESS('--- Finished Data Population ---'))

    def _populate_fleet(self):
        """Populates the FleetVehicle model."""
        self.stdout.write('Populating FleetVehicle data...')
        initial_fleet_data = [
            {'title': 'EKA 7', 'total_count': 12, 'active_count': 8, 'special': True, 'order': 1},
            {'title': 'EKA 9', 'total_count': 8, 'active_count': 6, 'special': False, 'order': 2},
            {'title': 'EKA 12', 'total_count': 5, 'active_count': 5, 'special': False, 'order': 3},
            {'title': 'EKA Low Floor', 'total_count': 10, 'active_count': 9, 'special': False, 'order': 4},
            {'title': 'EKA Coach', 'total_count': 3, 'active_count': 2, 'special': False, 'order': 5},
            {'title': 'EKA 2.5T', 'total_count': 15, 'active_count': 15, 'special': False, 'order': 6},
        ]

        created_count = 0
        for data in initial_fleet_data:
            _, created = FleetVehicle.objects.get_or_create(
                title=data['title'],
                defaults={
                    'total_count': data['total_count'],
                    'active_count': data['active_count'],
                    'special': data['special'],
                    'order': data['order'],
                }
            )
            if created:
                created_count += 1
        
        if created_count == 0:
            self.stdout.write(self.style.WARNING('Fleet data already exists. No new records created.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new fleet records.'))

    def _populate_performance(self):
        """Populates the PerformanceStat model."""
        self.stdout.write('Populating PerformanceStat data...')
        performance_data = [
            {'key': 'total_distance', 'title': 'Total Distance', 'value': '12,500 km', 'order': 1},
            {'key': 'co2_savings', 'title': 'CO2 Savings', 'value': '1.2 tons', 'order': 2},
            {'key': 'avg_energy_consumption', 'title': 'Avg. Energy Consumption', 'value': '0.8 kWh/km', 'order': 3},
            {'key': 'total_run_time', 'title': 'Total Run Time', 'value': '350 hrs', 'order': 4},
            {'key': 'traction_energy', 'title': 'Traction Energy', 'value': '10 MWh', 'order': 5},
            {'key': 'regen_energy', 'title': 'Regen. Energy', 'value': '1.5 MWh', 'order': 6},
        ]

        created_count = 0
        for data in performance_data:
            _, created = PerformanceStat.objects.get_or_create(
                key=data['key'],
                defaults={
                    'title': data['title'],
                    'value': data['value'],
                    'order': data['order'],
                }
            )
            if created:
                created_count += 1

        if created_count == 0:
            self.stdout.write(self.style.WARNING('Performance data already exists. No new records created.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new performance records.'))