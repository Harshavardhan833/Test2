from django.core.management.base import BaseCommand
from users.models import VehicleSummary, Vehicle

class Command(BaseCommand):
    """
    Custom Django management command to populate the database with initial data
    for the Vehicle Selection page. This command is idempotent, meaning it's
    safe to run multiple times without creating duplicate data.
    """
    help = 'Populates the database with initial data for the Vehicle Selection page.'

    def handle(self, *args, **options):
        """
        The main logic for the command. It creates a summary object for the
        'Eka 7' fleet and then creates several individual vehicle records
        associated with that summary.
        """
        self.stdout.write('Starting to populate Vehicle Selection data...')

        # --- Create or get the summary object for 'Eka 7' ---
        # Using get_or_create prevents creating duplicate summary objects if the
        # command is run more than once.
        summary, created = VehicleSummary.objects.get_or_create(
            fleet_type='Eka 7',
            defaults={
                'total_distance': '1280 km',
                'co2_savings': '150 kg',
                'avg_energy_consumption': '0.9 kWh',
                'run_time': '45 hrs',
                'traction_energy': '1.1 MWh',
                'regen_energy': '0.2 MWh',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created "Eka 7" summary object.'))
        else:
            self.stdout.write(self.style.WARNING('"Eka 7" summary already exists. Clearing old vehicles to repopulate.'))
            # If the summary already exists, we delete its old vehicles to ensure
            # the data is fresh and consistent with the definitions below.
            summary.vehicles.all().delete()

        # --- Data for individual vehicles to be created ---
        vehicles_to_create = [
            {'name': 'MH12 AB 1234', 'rating': '4.8', 'speed': 25, 'soc': 78, 'range': 90, 'temp': 32, 'address': 'Near Balewadi High Street, Pune'},
            {'name': 'MH14 CD 5678', 'rating': '4.5', 'speed': 0, 'soc': 92, 'range': 110, 'temp': 28, 'address': 'Parked at Baner, Pune'},
            {'name': 'MH01 EF 9101', 'rating': '4.9', 'speed': 40, 'soc': 65, 'range': 75, 'temp': 35, 'address': 'Enroute Hinjewadi Phase 3, Pune'},
        ]

        # --- Create the vehicle objects and link them to the summary ---
        for vehicle_data in vehicles_to_create:
            Vehicle.objects.create(summary=summary, **vehicle_data)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(vehicles_to_create)} vehicles for the "Eka 7" fleet.'))
