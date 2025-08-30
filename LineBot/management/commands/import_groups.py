import os
import json
from django.core.management.base import BaseCommand, CommandError
from LineBot.models import Group

class Command(BaseCommand):
    help = "Import groups from a JSON file"

    def handle(self, *args, **options):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        group_path = os.path.join(data_dir, 'Group.json')

        with open(group_path, encoding='utf-8') as f:
            groups = json.load(f)
            for item in groups:
                company = item['company']
                number = item['number']
                obj, created = Group.objects.get_or_create(
                    company=company,
                    number=number,
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Imported: {company} {number}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Already exists: {company} {number}"))