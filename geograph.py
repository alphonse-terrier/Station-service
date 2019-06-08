import openrouteservice
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from openrouteservice import convert


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
    print(coords)
    coords = ((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0]))
    geometry = client.directions(coords)['routes'][0]['geometry']
    decoded = convert.decode_polyline(geometry)
    list_position = decoded['coordinates']
    return (list_position)