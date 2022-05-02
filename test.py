from image_service.StreetViewImages import StreetViewImages
from pathlib import Path
from sys import exit

### Fill these in ###
origin = "274 Honeysuckle Way, Niceville, Florida 32578"
destination = "Walmart, Niceville, Florida"
#####################
if origin == "" or destination == "":
    exit('Fill in source and destination in app.py in the project root to generate a route')

try:
    api_key = Path('image_service/google_api_key.txt').read_text()
except Exception as e:
    print(e)
    exit('Make sure you have pasted your Google API key into a file called google_api_key.txt in the project root')

street_view_images = StreetViewImages(api_key)
gps_points = street_view_images.get_gps_points(origin, destination)
batches = street_view_images.create_params_batches(gps_points)
street_view_images.cache_images(batches)

print('Finished, cached images can be found in image_service/cache/')