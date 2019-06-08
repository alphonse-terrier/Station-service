import psycopg2
import json
import pandas as pd
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession, DataFrameReader
import pyspark.sql.functions as F

from pyspark import SparkContext
from geograph import *


def threshold(list_position, sensi):
    list_out = []

    for i in range(0, len(list_position)):
        if i % sensi == 0:
            list_out.append(list_position[i])

    '''
    for i in range(-1, -len(list_position), -1):
        if haversine(list_position[i], list_position[i-1]) >
    print(list_position)'''
    return (list_out)


f = open("credentials.json")
credentials = json.load(f)
f.close()

sc = SparkContext("local", "App Name")
sc.setLogLevel("WARN")
sql = SQLContext(sc)

def calculate(coords, fuel):


    conn = psycopg2.connect(host=credentials['rds_host'], user=credentials['username'],
                            password=credentials['password'], database=credentials['database'],
                            port=credentials['db_port'],
                            connect_timeout=10)

    df_stations = pd.read_sql("SELECT * FROM gas_stations", conn)

    spark = SparkSession.builder.getOrCreate()
    spark_df = sql.createDataFrame(df_stations)

    spark_df = spark_df.filter(f"{fuel} != 'NaN'")

    spark_df = spark_df.select("gasstationid", "latitude", "longitude", fuel)

    list_position = list_trajet(coords)
    thresh = threshold(list_position, 25)

    headers = ['Longitude_Road', 'Latitude_Road']

    thresh_pd = pd.DataFrame(thresh, columns=headers)
    road = spark.createDataFrame(thresh_pd)

    udf_haversine = F.udf(haversine)

    cross = spark_df.crossJoin(road)

    cross = cross.withColumn('Distance',
                             udf_haversine(cross.latitude, cross.longitude, cross.Latitude_Road, cross.Longitude_Road))

    cross = cross.filter(cross.Distance < 5)

    df = cross.select("gasstationid").toPandas().drop_duplicates()

    df = df.merge(df_stations, left_on='gasstationid', right_on='gasstationid')
    df = df.rename({fuel: 'prix'}, axis='columns')
    df['nom'] = df['address'] + r'<br />' + df['city'] + r'<br />Prix : ' + df['prix'].astype(str) + ' euros'
    print(df['nom'])
    df = df[['nom', 'latitude', 'longitude', 'prix']].sort_values('prix', ascending=True).head(8)
    print(df)
    return df


if __name__ == '__main__':
    depart = (-0.8833, 47.0667)
    arrivee = (48.26424, 48.8534)
    coords = (depart, arrivee)
    print(calculate(coords, 'sp95'))
