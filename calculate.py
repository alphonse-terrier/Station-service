from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark import SparkConf, SparkContext
from geograph import *
import time

conf = SparkConf().setAppName("Stations services").setMaster("local[2]")
sc = SparkContext(conf=conf)
sql = SQLContext(sc)
sql.sql("set spark.sql.shuffle.partitions=3")
spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

spark_df = spark.read.json("stations.json")
spark_df.createOrReplaceTempView("stations")


def threshold(list_position):
    '''Cette fonction permet de ne garder qu'un point tous les deux kilomètres'''
    list_out = [list_position[0]]

    for i in list_position:
        if haversine(i[0], i[1], list_out[-1][0], list_out[-1][1]) > 2:
            list_out.append(i)
    return (list_out)


def calculate(coords, fuel, distancemax, pompes):
    list_position = list_trajet(coords)
    thresh = threshold(list_position)
    headers = ['Longitude_Road', 'Latitude_Road']
    rdd = sc.parallelize(thresh)
    road = spark.createDataFrame(rdd, headers)

    viewstations = spark.sql(
        f"SELECT gasstationid, address, city, codepostal, latitude, longitude, {fuel} as prix FROM stations WHERE {fuel} is not null")

    udf_haversine = F.udf(haversine)

    cross = viewstations.crossJoin(road)

    cross = cross.withColumn('Distance',
                             udf_haversine(cross.latitude, cross.longitude, cross.Latitude_Road, cross.Longitude_Road))
    cross = cross.filter(cross.Distance < distancemax)

    gas_stat = cross.dropDuplicates(['gasstationid']).sort("prix")
    gas_stat = gas_stat.limit(min(pompes, gas_stat.count()))

    gas_stat.createOrReplaceTempView("stat")
    df = spark.sql("select * from stat").toPandas()
    return df


if __name__ == '__main__':
    start_time = time.time()
    calculate(((48.8706371, 2.3169393), (49.3601422, 0.0720105)), 'E10', 3, 10)
    print("Temps d'éxécution : %s secondes" % (time.time() - start_time))
