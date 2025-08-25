import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Report, VehicleRegistration, VehicleType

class Command(BaseCommand):
    help = 'Populates the database with initial data for the Reports page.'

    def handle(self, *args, **options):
        self.stdout.write('Populating Reports data...')
        Report.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing report data.'))

        # Ensure vehicle registrations exist (from populate_analysis command)
        if not VehicleRegistration.objects.exists():
            self.stdout.write(self.style.ERROR('No vehicle registrations found. Please run "populate_analysis" first.'))
            return

        registrations = list(VehicleRegistration.objects.all())
        report_types = ['Performance', 'Health', 'Charging', 'Fault']
        
        reports_to_create = []
        for _ in range(100): # Create 100 random reports
            reg = random.choice(registrations)
            report_type = random.choice(report_types)
            timestamp = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            report = Report(
                registration=reg,
                report_type=report_type,
                name=timestamp,
                col2=f"Val-{random.randint(10, 99)}",
                signal=f"Sig-{random.randint(100, 999)}",
                signal0=f"S0-{random.randint(0,1)}",
                signal1=f"S1-{random.randint(0,1)}",
                signal2=f"S2-{random.randint(0,1)}"
            )
            reports_to_create.append(report)
        
        Report.objects.bulk_create(reports_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(reports_to_create)} reports.'))
