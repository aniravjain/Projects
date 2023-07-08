import datetime
import os

yesterday = datetime.date.today() - datetime.timedelta(days=1)


### info needed to access instantiate PRAW reddit object ###

### Information deleted for security reasons
client_id=""
client_secret=""
user_agent=""
password=""
username=""

### gcs bucket data ###

bucket_name = os.environ.get("GS_BUCKET_NAME")
service_account_key_file = os.environ.get("GS_SERVICE_ACCOUNT_KEY_FILE")

### mongo data ###

mongo_username = os.environ.get("MONGO_USERNAME")
mongo_password =  os.environ.get("MONGO_PASSWORD")
mongo_ip_address = os.environ.get("MONGO_IP")
database_name = os.environ.get("MONGO_DB_NAME")
collection_name_1 = 'posts'
collection_name_2 = 'comments'
