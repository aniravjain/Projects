import os
import pandas as pd
import praw


from google.cloud import storage

from user_definition import *

def praw_setup(client_id, client_secret, user_agent, password, username):
    '''
    Instantiate the Python Reddit API Wrapper (PRAW)
    object in order to access Reddit data.
    
    client_id = client_id from your app info on 
        Reddit's dev website
    client_secret = client_secret from from your
        app info on Reddit's dev website
    user_agent = A string representing whoever is
        accessing the data. Per Reddit's API rules,
        must include your Reddit username.
    password = Your reddit account's password.
    username = Your reddit username.
    '''
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        password=password,
        username=username
    )
    return reddit


def get_post_titles_and_features(reddit, post_limit, timeframe='day', one_sub=False, sub=None):
    '''
    Obtain the top n (post_limit) posts in the requested 
    timeframe on all 11 subreddits, as well as desired attributes. Can also specify if 
    just want post info on one subreddit.
    
    reddit = PRAW instance
    post_limit = # of posts you want to get
    timeframe = hour, day (the default), week, month, year, 
        or all (which is all time)
    one_sub = If True, gathers data on specific subreddit.
    sub = Specific subreddit to get data.
    '''
    if one_sub == True:
        table = []
        for submission in reddit.subreddit(sub).top(limit=post_limit, time_filter=timeframe):
            table.append([submission.id,
                            submission.title,
                            submission.subreddit.display_name,
                            datetime.datetime.utcfromtimestamp(submission.created_utc),
                            submission.score,
                            submission.num_comments,
                            submission.total_awards_received])
        return pd.DataFrame(table, columns=['post_id', 'post_title', 'post_subreddit',
                                           'creation_datetime', 'score', 'num_comments', 'total_awards_received'])
    else:
        subreddits = ['conservative', 'coronavirus', 'worldnews', 'politics', 'economics',
                      'technology', 'entertainment', 'science', 'news', 'health', 'environment']
        table = []
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).top(limit=post_limit, time_filter=timeframe):
                table.append([submission.id,
                            submission.title,
                            submission.subreddit.display_name,
                            datetime.datetime.utcfromtimestamp(submission.created_utc),
                            submission.score,
                            submission.num_comments,
                            submission.total_awards_received])
        return pd.DataFrame(table, columns=['post_id', 'post_title', 'post_subreddit',
                                           'creation_datetime', 'score', 'num_comments', 'total_awards_received'])
    
def get_comments_and_features(reddit, post_limit, timeframe='day', one_sub=False, sub=None):
    """
    Obtain the top n posts' comments from 11 particular subreddits
    in requested timeframe, as well as desired attributes.
    
    reddit = PRAW instance
    post_limit = # of desired posts
    timeframe = hour, day (the default), week, month, year, 
        or all (which is all time)
    one_sub = If True, gathers data on specific subreddit.
    sub = Specific subreddit to get data.
    """
    if one_sub == True:
        table = []
        for submission in reddit.subreddit(sub).top(limit=post_limit, time_filter=timeframe):
            comments = submission.comments[:-1] # not taking into account the MoreComments object
            for comment in comments:
                table.append([submission.id,
                                comment.id,
                                comment.body,
                                submission.subreddit.display_name,
                                datetime.datetime.utcfromtimestamp(comment.created_utc),
                                comment.score])
        return pd.DataFrame(table, columns = ['post_id', 'comment_id', 'comment_text',
                                              'subreddit', 'creation_datetime', 'comment_karma'])
    else:
        subreddits = ['conservative', 'coronavirus', 'worldnews', 'politics', 'economics',
                      'technology', 'entertainment', 'science', 'news', 'health', 'environment']
        table = []
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).top(limit=post_limit, time_filter=timeframe):
                comments = submission.comments[:-1] # not taking into account the MoreComments object
                for comment in comments:
                    table.append([submission.id,
                                             comment.id,
                                             comment.body,
                                             submission.subreddit.display_name,
                                             datetime.datetime.utcfromtimestamp(comment.created_utc),
                                             comment.score])
        return pd.DataFrame(table, columns = ['post_id', 'comment_id', 'comment_text',
                                              'subreddit', 'creation_datetime', 'comment_karma'])

def write_csv_to_gcs(bucket_name, blob_name, service_account_key_file, df):
    '''
    Write and read a blob from GCS using file-like IO.
    Writes the dataframe (df) as a CSV file.
    '''
    storage_client = storage.Client.from_service_account_json(service_account_key_file)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    with blob.open('w') as f:
        df.to_csv(f, index=False)
        

