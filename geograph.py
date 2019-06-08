import openrouteservice
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from openrouteservice import convert
import numpy as np


def whereitis(address):
    geolocator = Nominatim(user_agent="stationservice")
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude)


AVG_EARTH_RADIUS = 6371  # in km
MILES_PER_KILOMETER = 0.621371


def haversine(lat1, lng1, lat2, lng2, miles=False):
    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * MILES_PER_KILOMETER  # in miles
    else:
        return h  # in kilometers


client = openrouteservice.Client(
    key='5b3ce3597851110001cf6248c65425cfab7e40539af9e1987459f8e4')  # Specify your personal API key


def list_trajet(coords):
    coords = ((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0]))
    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    list_position = decoded['coordinates']
    return (list_position)


def getBoundsZoomLevel(coords):
    """
    source: https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
    :param bounds: list of ne and sw lat/lon
    :param mapDim: dictionary with image size in pixels
    :return: zoom level to fit bounds in the visible area
    """
    mapDim={'height': 700, 'width': 520}
    sw_lat = coords[0][0]
    sw_long = coords[0][1]
    ne_lat = coords[1][0]
    ne_long = coords[1][1]

    scale = 2  # adjustment to reflect MapBox base tiles are 512x512 vs. Google's 256x256
    WORLD_DIM = {'height': 256 * scale, 'width': 256 * scale}
    ZOOM_MAX = 18

    def latRad(lat):
        sin = np.sin(lat * np.pi / 180)
        radX2 = np.log((1 + sin) / (1 - sin)) / 2
        return max(min(radX2, np.pi), -np.pi) / 2

    def zoom(mapPx, worldPx, fraction):
        return np.floor(np.log(mapPx / worldPx / fraction) / np.log(2))

    latFraction = (latRad(ne_lat) - latRad(sw_lat)) / np.pi

    lngDiff = ne_long - sw_long
    lngFraction = ((lngDiff + 360) if lngDiff < 0 else lngDiff) / 360
    print(mapDim['height'], WORLD_DIM['height'], latFraction, mapDim['width'], WORLD_DIM['width'], lngFraction)
    latZoom = zoom(mapDim['height'], WORLD_DIM['height'], latFraction)
    lngZoom = zoom(mapDim['width'], WORLD_DIM['width'], lngFraction)

    return min(latZoom, lngZoom, ZOOM_MAX)


if __name__ == '__main__':
    depart = ((47.0667 , -0.8), (47.4833, 2.5333))
    print(getBoundsZoomLevel(depart, {'height': 700, 'width': 520}))
