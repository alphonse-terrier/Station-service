import openrouteservice
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from openrouteservice import convert

geolocator = Nominatim(user_agent="stationservice")


def whereitis(address):
    """Cette focntion permet de géocoder une adresse en latitude/longitude"""
    latitude, longitude = None, None
    try:
        location = geolocator.geocode(address)
        if 'France' in location.address:
            latitude, longitude = location.latitude, location.longitude
    except AttributeError:
        pass
    return (latitude, longitude)


AVG_EARTH_RADIUS = 6371  # in km
MILES_PER_KILOMETER = 0.621371


def haversine(lat1, lng1, lat2, lng2, miles=False):
    """Cette fonction permet de calculer la distance kilométrique entre deux latitudes/longitudes"""
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * MILES_PER_KILOMETER
    else:
        return h


client = openrouteservice.Client(
    key='5b3ce3597851110001cf6248c65425cfab7e40539af9e1987459f8e4')


def list_trajet(coords):
    """Cette fonction permet de générer une liste avec l'itinéraire du trajet entre les deux points donnés en entrée"""
    coords = ((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0]))
    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    list_position = decoded['coordinates']
    return (list_position)


if __name__ == '__main__':
    depart = ((47.0667, -0.8), (47.4833, 2.5333))
    # print(getBoundsZoomLevel(depart, {'height': 700, 'width': 520}))
