from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import OfficerProfile

class Command(BaseCommand):
    help = 'Seeds initial pre-authorized Legal Metrology Officers for testing and verification'

    def handle(self, *args, **options):
        officers_data = [
            {
                'username': 'admin_officer',
                'email': 'admin.metrology@nic.in',
                'password': 'OfficerAdmin@2024',
                'is_staff': True,
                'is_superuser': True,
                'officer_id': 'OFF-ADMIN-001',
                'name': 'Tushar Rathore',
                'designation': 'Joint Director / Legal Metrology Controller',
                'department': 'Department of Consumer Affairs, Legal Metrology Division',
                'jurisdiction': 'National Headquarters, New Delhi',
                'role': 'ADMIN',
                'phone': '+91-11-23380001',
                'is_active': True,
            },
            {
                'username': 'inspector_delhi',
                'email': 'vivek.metrology@delhi.gov.in',
                'password': 'Inspector@123',
                'is_staff': False,
                'is_superuser': False,
                'officer_id': 'OFF-DEL-2024-001',
                'name': 'vivek kumar',
                'designation': 'Senior Inspector of Legal Metrology',
                'department': 'Department of Consumer Affairs, Delhi Enforcement Wing',
                'jurisdiction': 'Zone-1, North Delhi',
                'role': 'INSPECTOR',
                'phone': '+91-9876543210',
                'is_active': True,
            },
            {
                'username': 'inspector_mumbai',
                'email': 'pooja.metrology@maharashtra.gov.in',
                'password': 'Inspector@123',
                'is_staff': False,
                'is_superuser': False,
                'officer_id': 'OFF-MUM-2024-042',
                'name': 'Pooja Sharma',
                'designation': 'Inspector of Legal Metrology',
                'department': 'Controllerate of Legal Metrology, Maharashtra',
                'jurisdiction': 'Zone-4, Mumbai Central',
                'role': 'INSPECTOR',
                'phone': '+91-9876543211',
                'is_active': True,
            },
            {
                'username': 'inspector_inactive',
                'email': 'vikram.metrology@rajasthan.gov.in',
                'password': 'Inspector@123',
                'is_staff': False,
                'is_superuser': False,
                'officer_id': 'OFF-INACT-2024-099',
                'name': 'Vikram Singh (Inactive)',
                'designation': 'Suspended Inspector',
                'department': 'Department of Legal Metrology, Rajasthan',
                'jurisdiction': 'Zone-2, Jaipur West',
                'role': 'INSPECTOR',
                'phone': '+91-9876543212',
                'is_active': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in officers_data:
            user, created = User.objects.get_or_create(
                username=item['username'],
                defaults={
                    'email': item['email'],
                    'is_staff': item['is_staff'],
                    'is_superuser': item['is_superuser'],
                    'is_active': item['is_active'],
                }
            )
            # Ensure password is set with secure hashing
            user.set_password(item['password'])
            user.email = item['email']
            user.is_staff = item['is_staff']
            user.is_superuser = item['is_superuser']
            user.is_active = item['is_active']
            user.save()

            profile, prof_created = OfficerProfile.objects.update_or_create(
                officer_id=item['officer_id'],
                defaults={
                    'user': user,
                    'name': item['name'],
                    'designation': item['designation'],
                    'department': item['department'],
                    'jurisdiction': item['jurisdiction'],
                    'role': item['role'],
                    'phone': item['phone'],
                    'is_active': item['is_active'],
                }
            )

            if created or prof_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created officer: {item['officer_id']} ({item['name']})"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated officer: {item['officer_id']} ({item['name']})"))

        self.stdout.write(self.style.SUCCESS(
            f"\nFinished seeding officers. Created: {created_count}, Updated: {updated_count}\n"
            "Pre-authorized test credentials:\n"
            "  1. Active Inspector (Delhi):  Officer ID: OFF-DEL-2024-001  | Password: Inspector@123\n"
            "  2. Active Inspector (Mumbai): Officer ID: OFF-MUM-2024-042  | Password: Inspector@123\n"
            "  3. Inactive Officer (Rejection test): Officer ID: OFF-INACT-2024-099 | Password: Inspector@123\n"
            "  4. Administrator:             Officer ID: OFF-ADMIN-001     | Password: OfficerAdmin@2024\n"
        ))
