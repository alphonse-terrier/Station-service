import openrouteservice
from openrouteservice import convert

coords = ((8.34234, 48.23424), (8.34423, 48.26424))

client = openrouteservice.Client(key='5b3ce3597851110001cf6248c65425cfab7e40539af9e1987459f8e4') # Specify your personal API key

geometry = client.directions(coords)['routes'][0]['geometry']

decoded = convert.decode_polyline(geometry)

print(len(decoded['coordinates']))
print(decoded['coordinates'])