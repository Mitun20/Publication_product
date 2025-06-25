import requests
from time import sleep

LOCATIONIQ_API_KEY = "pk.2d7d5827520fc2b45cb592102edd76be"  # replace with your actual key

def geocode_location_iq(address):
    url = f"https://us1.locationiq.com/v1/search.php?key={LOCATIONIQ_API_KEY}&q={address}&format=json"
    headers = {"User-Agent": "DjangoApp"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        elif response.status_code == 429:
            sleep(1)
            return geocode_location_iq(address)
    except Exception as e:
        print(f"Geocode error for {address}: {e}")
    return None, None
