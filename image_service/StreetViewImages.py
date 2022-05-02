from googlemaps import Client
from polyline import decode
from google_streetview.api import results
from geographiclib.geodesic import Geodesic
from os.path import isdir
from pathlib import Path
from shutil import rmtree

class StreetViewImages:
    """Plot a route, convert it into a list of gps coord tuples, and download street view images from a few different angles"""
    def __init__(self, api_key):
        self.api_key = api_key

    def get_gps_points(self, origin, destination):
        """Request directions and extract GPS coords from results"""
        gmaps = Client(key=self.api_key)
        directions_result = gmaps.directions(origin, destination, mode="driving")
        pl = directions_result[0]['overview_polyline']['points']
        gps_points = decode(pl, geojson=True)
        return gps_points

    def create_params_batches(self, gps_points):
        """Create params to request an image per gps_point obtained.  Batch size is capped at 100, I can't remember if that's actually true or if I'm just paranoid"""
        params = []
        origin = gps_points[0]
        batches = []
        for index, point in enumerate(gps_points):
            if point == origin:
                point = gps_points[index + 1]
            else:
                origin = gps_points[index - 1]

            # Calculate heading
            lon0 = origin[0]
            lat0 = origin[1]

            lon1 = point[0]
            lat1 = point[1]

            heading = Geodesic.WGS84.Inverse(lat0, lon0, lat1, lon1)['azi1']

            # Insert values into a new param object and start a new batch if necessary
            param = {}
            param['location'] = f'{lat0}, {lon0}'
            param['key'] = self.api_key
            param['size'] = '640x640'
            param['heading'] = heading
            param['pitch'] = 0
            params.append(param)

            if len(params) > 99:
                batches.append(params)
                params = []

        batches.append(params)
        return batches
    
    def cache_images(self, batches, download_directory=f'{Path(__file__).parent}/cache'):
        """Grabs images and downloads them to the cache one batch at a time"""
        # Clear the download directory before downloading
        if isdir(download_directory):
            rmtree(download_directory)
        for batch in batches:
            print('Requesting links to street view images')
            result = results(batch)
            print('Downloading images to cache')
            result.download_links(download_directory)