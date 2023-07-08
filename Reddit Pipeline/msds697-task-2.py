import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from reddit_calls import *
from user_definition import *

def _download_reddit_data():
    """
    Create reddit instance and collect data to write to gcs as two csv's,
    one for posts, and the other for comments on those posts.
    """
    reddit = praw_setup(client_id, client_secret, user_agent, password, username)
    blob_name_posts = f'{yesterday}/posts.csv' # names for the files
    blob_name_comments = f'{yesterday}/comments.csv'
    
    df_posts = get_post_titles_and_features(reddit, post_limit=100, timeframe='day', one_sub=False, sub=None)
    df_comments = get_comments_and_features(reddit, post_limit=100, timeframe='day', one_sub=False, sub=None)
    
    write_csv_to_gcs(bucket_name, blob_name_posts, service_account_key_file, df_posts)
    write_csv_to_gcs(bucket_name, blob_name_comments, service_account_key_file, df_comments)

with DAG(
    dag_id="msds697_task_2",
    schedule_interval='@daily',
    start_date=datetime.datetime(2023, 2, 25),
    end_date=datetime.datetime(2023, 3, 10),
    catchup=False
    ) as dag:
    
    
    
    create_insert_aggregate = SparkSubmitOperator(
        task_id="aggregate_creation",
        packages="com.google.cloud.bigdataoss:gcs-connector:hadoop2-1.9.17,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
        exclude_packages="javax.jms:jms,com.sun.jdmk:jmxtools,com.sun.jmx:jmxri",
        conf={"spark.driver.userClassPathFirst":True,
             "spark.executor.userClassPathFirst":True
             # "spark.hadoop.fs.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
             # "spark.hadoop.fs.AbstractFileSystem.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
             # "spark.hadoop.fs.gs.auth.service.account.enable":True,
             # "google.cloud.auth.service.account.json.keyfile":service_account_key_file
             },
        verbose=True,
        application='agg_to_mongo.py'
    )
    
    download_reddit_data = PythonOperator(task_id='download_reddit_data',
                                           python_callable=_download_reddit_data,
                                         dag=dag)
    
    download_reddit_data >> create_insert_aggregate