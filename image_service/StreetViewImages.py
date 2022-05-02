import googlemaps
import polyline
import google_streetview.api
from geographiclib.geodesic import Geodesic
import os

class StreetViewImages:
    """Plot a route, convert it into a list of gps coord tuples, and download street view images from a few different angles"""
    def __init__(self, api_key):
        self.api_key = api_key

    def get_gps_points(self, origin, destination):
        """Request directions and extract GPS coords from results"""
        # now = datetime.now()
        gmaps = googlemaps.Client(key=self.api_key)
        directions_result = gmaps.directions(origin, destination, mode="driving")#  departure_time=now)
        pl = directions_result[0]['overview_polyline']['points']
        gps_points = polyline.decode(pl, geojson=True)
        return gps_points

    def create_params_batches(self, gps_points):
        """Create params for batch request.  Size is capped at 100, I can't remember if that's actually true or if I'm just paranoid"""
        params = []
        origin = gps_points[0]
        # debuginfo = []
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
            # debug = {'lat0': lat0, 'lon0': lon0, 'lat1': lat1, 'lon1': lon1, 'heading': heading}
            # debuginfo.append(debug)

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
    
    def cache_images(self, batches, download_directory=f'{os.getcwd()}/images/cache/'):
        for batch in batches:
            result = google_streetview.api.results(batch)
            result.download_links(download_directory)