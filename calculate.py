import openrouteservice
from openrouteservice import convert
import psycopg2
import json
import pandas as pd
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from math import radians, cos, sin, asin, sqrt
from pyspark import SparkContext

sc = SparkContext("local", "App Name")
sql = SQLContext(sc)

f = open("credentials.json")
credentials = json.load(f)
f.close()

conn = psycopg2.connect(host=credentials['rds_host'], user=credentials['username'], password=credentials['password'], database=credentials['database'], port=credentials['db_port'],
                        connect_timeout=10)

df_stations = pd.read_sql("SELECT * FROM gas_stations", conn)

spark= SparkSession.builder.getOrCreate()
spark_df = sql.createDataFrame(df_stations)

spark_df.registerTempTable("stations_services")
#spark_df.show(10)


def haversine(lat1, lng1, lat2, lng2, miles=False):
    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * MILES_PER_KILOMETER # in miles
    else:
        return h  # in kilometers



depart = (-0.8833, 47.0667)
arrivee = (48.26424, 48.8534)
coords = (depart, arrivee)

client = openrouteservice.Client(key='5b3ce3597851110001cf6248c65425cfab7e40539af9e1987459f8e4') # Specify your personal API key

geometry = client.directions(coords)['routes'][0]['geometry']

decoded = convert.decode_polyline(geometry)
list_position = decoded['coordinates']


AVG_EARTH_RADIUS = 6371  # in km
MILES_PER_KILOMETER = 0.621371

def threshold(list_position):
    list_out = []

    for i in range(0, len(list_position)):
        if i%14 == 0:
            list_out.append(list_position[i])
    '''
    for ind in range(-1, -len(list_position), -1):
        break
        #print(ind)
        #if haversine(list_position[ind], list_position)
    '''
    return(list_out)

thresh = threshold(list_position)




headers = ['Longitude_Road', 'Latitude_Road']

thresh_pd = pd.DataFrame(thresh, columns=headers)
road = spark.createDataFrame(thresh_pd)


udf_haversine = F.udf(haversine)

cross = spark_df.crossJoin(road)

cross = cross.withColumn('Distance', udf_haversine(cross.latitude, cross.longitude, cross.Latitude_Road, cross.Longitude_Road))


cross = cross.filter(cross.Distance < 4)
#cross.show(15)

df = cross.select("gasstationid").toPandas().drop_duplicates()
print(df)

'''
for pos in thresh:
    print(haversine(pos, arrivee))
'''
