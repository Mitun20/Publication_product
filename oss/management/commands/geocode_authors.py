from django.core.management.base import BaseCommand
from oss.models import Author
import requests
import time

class Command(BaseCommand):
    help = 'Geocode authors and save lat/lon'

    def handle(self, *args, **kwargs):
        authors = Author.objects.filter(latitude__isnull=True, country__isnull=False)
        for author in authors:
            address = ', '.join(filter(None, [author.city, author.state, author.country.country]))
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
            try:
                resp = requests.get(url, headers={'User-Agent': 'YourApp/1.0'}, timeout=10)
                data = resp.json()
                if data:
                    author.latitude = float(data[0]['lat'])
                    author.longitude = float(data[0]['lon'])
                    author.save()
                    self.stdout.write(self.style.SUCCESS(f"Geocoded: {address}"))
                else:
                    self.stdout.write(self.style.WARNING(f"No result for: {address}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error for {address}: {e}"))
            time.sleep(1.1)  # Respect Nominatim rate limit