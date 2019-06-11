import psycopg2
import json
import pandas as pd
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession, DataFrameReader
import pyspark.sql.functions as F

from pyspark import SparkConf, SparkContext
from geograph import *


def threshold(list_position):
    list_out = [list_position[0]]

    for i in list_position:
        if haversine(i[0], i[1], list_out[-1][0], list_out[-1][1]) > 2:
            list_out.append(i)
    return (list_out)


f = open("credentials.json")
credentials = json.load(f)
f.close()

conf = SparkConf().setAppName("Stations services").setMaster("local[*]")
sc = SparkContext(conf=conf)
sql = SQLContext(sc)

def calculate(coords, fuel, distancemax, pompes):
    spark = SparkSession.builder.getOrCreate()
    spark_df = spark.read.json("stations.json")
    spark_df.createOrReplaceTempView("stations")

    #spark_df = spark_df.filter(f"{fuel} != 'NaN'")
    viewStations = spark.sql(f"SELECT gasstationid, address, city, codepostal, latitude, longitude, {fuel} as prix FROM stations WHERE {fuel} is not null")

    list_position = list_trajet(coords)
    thresh = threshold(list_position)
    rdd = sc.parallelize(thresh)

    headers = ['Longitude_Road', 'Latitude_Road']

    road = spark.createDataFrame(rdd, headers)

    udf_haversine = F.udf(haversine)

    cross = viewStations.crossJoin(road)

    cross = cross.withColumn('Distance',
                             udf_haversine(cross.latitude, cross.longitude, cross.Latitude_Road, cross.Longitude_Road))
    cross = cross.filter(cross.Distance < distancemax)

    gas_stat = cross.select('gasstationid').dropDuplicates()
    df = gas_stat.join(viewStations, gas_stat.gasstationid == viewStations.gasstationid, how='left').sort("prix")
    df = df.limit(min(pompes, df.count()))

    return df.toPandas()


if __name__ == '__main__':
    depart = (-0.8833, 47.0667)
    arrivee = (48.26424, 48.8534)
    calculate(((48.8706371, 2.3169393), (49.3601422, 0.0720105)), 'E10', 3, 10)
