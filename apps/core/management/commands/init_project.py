import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
import json

from apps.wilayas.models import Commune, Wilaya
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Initialize the project by loading locations and other setup tasks"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting project init process..."))
        subprocess.run("python manage.py migrate", shell=True, check=True)
        self.create_superuser()
        self.load_wilayas()
        self.load_communes()
        # subprocess.run(
        #     "python manage.py loaddata fixtures/sample_data.json",
        #     shell=True,
        #     check=True,
        # )

        self.stdout.write(self.style.SUCCESS("Project Inited completed successfully!"))

    def create_superuser(self):
        User = get_user_model()
        if not User.objects.filter(email="admin@admin.com").exists():
            User.objects.create_superuser(email="admin@admin.com", password="admin")
            self.stdout.write(self.style.SUCCESS("Superuser created successfully!"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))

    def load_wilayas(self):
        self.stdout.write(self.style.SUCCESS("Loading wilayas..."))
        wilayas_path = os.path.join(settings.BASE_DIR, "fixtures", "wilayas.json")
        with open(wilayas_path, encoding="utf-8") as f:
            wilayas_data = json.load(f)

        wilaya_objs = [
            Wilaya(
                id=int(w["id"]),
                code=w["code"],
                name=w["name"],
                ar_name=w["ar_name"],
                longitude=float(w["longitude"]),
                latitude=float(w["latitude"]),
            )
            for w in wilayas_data
        ]

        Wilaya.objects.bulk_create(wilaya_objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS("Locations loaded successfully!"))

    def load_communes(self):
        self.stdout.write(self.style.SUCCESS("Loading communes..."))
        communes_path = os.path.join(settings.BASE_DIR, "fixtures", "communes.json")
        with open(communes_path, encoding="utf-8") as f:
            communes_data = json.load(f)
        communes_objs = [
            Commune(
                id=int(c["id"]),
                wilaya_id=int(c["wilaya_id"]),
                name=c["name"],
                postal_code=c.get("postal_code", ""),
                ar_name=c.get("ar_name", ""),
                longitude=float(c.get("longitude", 0)),
                latitude=float(c.get("latitude", 0)),
                is_active=c.get("is_active", True),
            )
            for c in communes_data
        ]
        Commune.objects.bulk_create(communes_objs, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Communes loaded successfully!"))
