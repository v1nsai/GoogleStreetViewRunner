from image_service.StreetViewImages import StreetViewImages
from pathlib import Path

if __name__ == '__main__':
    origin = "2402 Southgate Square, Reston, VA 20191"
    destination = "11900 Market Street, Reston, VA 20190"
    api_key = Path('image_service/google_api_key.txt').read_text()

    street_view_images = StreetViewImages(api_key)
    gps_points = street_view_images.get_gps_points(origin, destination)
    batches = street_view_images.create_params_batches(gps_points)
    street_view_images.cache_images(batches)

    print('Finished')