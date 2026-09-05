import os

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from users.models import OfficerProfile


class Command(BaseCommand):
    help = "Seeds pre-authorized Legal Metrology Officers without resetting existing passwords."

    officers_data = [
        {
            "username": "admin_officer",
            "email": "admin.metrology@nic.in",
            "password_env": "OFFICER_01_PASSWORD",
            "is_staff": True,
            "is_superuser": True,
            "officer_id": "OFF-ADMIN-001",
            "name": "Tushar Rathore",
            "designation": "Joint Director / Legal Metrology Controller",
            "department": "Department of Consumer Affairs, Legal Metrology Division",
            "jurisdiction": "National Headquarters, New Delhi",
            "role": "ADMIN",
            "phone": "+91-11-23380001",
            "is_active": True,
        },
        {
            "username": "inspector_delhi",
            "email": "vivek.metrology@delhi.gov.in",
            "password_env": "OFFICER_02_PASSWORD",
            "is_staff": False,
            "is_superuser": False,
            "officer_id": "OFF-DEL-2024-001",
            "name": "vivek kumar",
            "designation": "Senior Inspector of Legal Metrology",
            "department": "Department of Consumer Affairs, Delhi Enforcement Wing",
            "jurisdiction": "Zone-1, North Delhi",
            "role": "INSPECTOR",
            "phone": "+91-9876543210",
            "is_active": True,
        },
        {
            "username": "inspector_mumbai",
            "email": "dev.metrology@maharashtra.gov.in",
            "password_env": "OFFICER_03_PASSWORD",
            "is_staff": False,
            "is_superuser": False,
            "officer_id": "OFF-MUM-2024-042",
            "name": "dev dogra",
            "designation": "Inspector of Legal Metrology",
            "department": "Controllerate of Legal Metrology, Maharashtra",
            "jurisdiction": "Zone-4, Mumbai Central",
            "role": "INSPECTOR",
            "phone": "+91-9876543211",
            "is_active": True,
        },
        {
            "username": "inspector_inactive",
            "email": "vikram.metrology@rajasthan.gov.in",
            "password_env": "OFFICER_04_PASSWORD",
            "is_staff": False,
            "is_superuser": False,
            "officer_id": "OFF-INACT-2024-099",
            "name": "Vikram Singh (Inactive)",
            "designation": "Suspended Inspector",
            "department": "Department of Legal Metrology, Rajasthan",
            "jurisdiction": "Zone-2, Jaipur West",
            "role": "INSPECTOR",
            "phone": "+91-9876543212",
            "is_active": False,
        },
    ]

    def handle(self, *args, **options):
        missing = [
            item["password_env"]
            for item in self.officers_data
            if not os.environ.get(item["password_env"])
        ]
        if missing:
            names = ", ".join(missing)
            raise CommandError(f"Missing required officer password environment variable(s): {names}")

        created_count = 0
        existing_count = 0

        with transaction.atomic():
            for item in self.officers_data:
                user, created = User.objects.get_or_create(
                    username=item["username"],
                    defaults={
                        "email": item["email"],
                        "is_staff": item["is_staff"],
                        "is_superuser": item["is_superuser"],
                        "is_active": item["is_active"],
                    },
                )
                if created:
                    user.set_password(os.environ[item["password_env"]])
                user.email = item["email"]
                user.is_staff = item["is_staff"]
                user.is_superuser = item["is_superuser"]
                user.is_active = item["is_active"]
                user.save()

                _, profile_created = OfficerProfile.objects.update_or_create(
                    officer_id=item["officer_id"],
                    defaults={
                        "user": user,
                        "name": item["name"],
                        "designation": item["designation"],
                        "department": item["department"],
                        "jurisdiction": item["jurisdiction"],
                        "role": item["role"],
                        "phone": item["phone"],
                        "is_active": item["is_active"],
                    },
                )

                if created or profile_created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Officer {item['officer_id']} created successfully."))
                else:
                    existing_count += 1
                    self.stdout.write(f"Officer {item['officer_id']} already exists; password unchanged.")

        self.stdout.write(self.style.SUCCESS(
            f"Finished seeding officers. Created: {created_count}, Existing: {existing_count}."
        ))
