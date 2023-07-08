import io
import pandas as pd

from google.cloud import storage
from mongodb import *
from pyspark.sql import Row, SparkSession

from user_definition import *


def return_csv_data(spark, service_account_key_file,
                bucket_name, date, file):
    storage_client = storage.Client.from_service_account_json(service_account_key_file)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f'{date}/{file}.csv')
    csv_str = blob.download_as_string().decode("utf8")
    df = pd.read_csv(io.StringIO(csv_str))
    df = spark.createDataFrame(df)
    return df


def insert_aggregates_to_mongo():
    spark = SparkSession.builder.getOrCreate()
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    conf.set("google.cloud.auth.service.account.json.keyfile", service_account_key_file)
    conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    conf.set("fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    
    # conf = pyspark.SparkConf().set("spark.jars", jar_path)
    # sc = spark.sparkContext
    # conf = sc._jsc.hadoopConfiguration()
    # conf.set("fs.gs.impl","com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    # conf.set("google.cloud.auth.service.account.json.keyfile", service_account_key_file)
    
    # spark = SparkSession.builder\
    # .config('spark.hadoop.fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')\
    # .config('spark.hadoop.fs.AbstractFileSystem.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')\
    # .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true')\
    # .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', '/path/to/keyfile.json')\
    # .getOrCreate()

# Load the CSV file into a Spark DataFrame

    df_posts = return_csv_data(spark,
                               service_account_key_file,
                                 bucket_name,
                                 yesterday,
                                 'posts')
    
    df_comments = return_csv_data(spark,
                                  service_account_key_file,
                                 bucket_name,
                                 yesterday,
                                 'comments')

    aggregate_posts = df_posts.rdd.map(lambda row: row.asDict()).collect()
    aggregate_comments = df_comments.rdd.map(lambda row: row.asDict()).collect()

    mongodb_posts = MongoDBCollection(mongo_username,
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name_1)
    
    mongodb_comments = MongoDBCollection(mongo_username,
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name_2)

    for aggregate in aggregate_posts:
        mongodb_posts.insert_one(aggregate)
        
    for aggregate in aggregate_comments:
        mongodb_comments.insert_one(aggregate)

if __name__=="__main__":
    insert_aggregates_to_mongo()
