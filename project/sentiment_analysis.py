#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 15:36:47 2019

@author: rimzimthube
"""

'''
Command used in terminal:
spark-submit MS/LSA/Project/Test/untitled7.WebsiteConsumer.py localhost 9009


'''

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row,SQLContext
import sys
import requests

def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)

def get_sql_context_instance(spark_context):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']
def process_rdd(time, rdd):
    print("----------- %s -----------" % str(time))
    try:
        # Get spark sql singleton context from the current context
        sql_context = get_sql_context_instance(rdd.context)
        # convert the RDD to Row RDD
        print('sql context')
        row_rdd = rdd.map(lambda w: Row(hashtag=w[0], hashtag_count=w[1]))
        print('row rdd')
        # create a DF from the Row RDD
        hashtags_df = sql_context.createDataFrame(row_rdd)
        # Register the dataframe as table
        hashtags_df.registerTempTable("hashtags")
        print('hashtag df')
        # get the top 10 hashtags from the table using SQL and print them
        hashtag_counts_df = sql_context.sql("select hashtag, hashtag_count from hashtags order by hashtag_count desc limit 10")
        print('count')
        
        top_tags = [str(t.hashtag) for t in hashtag_counts_df.select("hashtag").collect()]
        tags_count = [p.hashtag_count for p in hashtag_counts_df.select("hashtag_count").collect()]
        print(top_tags)
        print(tags_count)
        # call this method to prepare top 10 hashtags DF and send them
        send_df_to_dashboard(hashtag_counts_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)
        
def process_string(time,rdd):
    print("----------- %s -----------" % str(time))
    try:
        # Get spark sql singleton context from the current context
        sql_context = get_sql_context_instance(rdd.context)
        # convert the RDD to Row RDD
        row_rdd = rdd.map(lambda w: Row(Tweet=w))
        # create a DF from the Row RDD
        frame=row_rdd.toDF()
#        hashtags_df = sql_context.createDataFrame(row_rdd)
        print("createddataframe")
        print(format(frame))
        
        # Register the dataframe as table
#        hashtags_df.registerTempTable("hashtags")
        # get the top 10 hashtags from the table using SQL and print them
#        hashtag_counts_df = sql_context.sql("select Tweet from hashtags")
#        hashtag_counts_df.show()
        # call this method to prepare top 10 hashtags DF and send them
        send_df_to_dashboard(hashtag_counts_df)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def send_df_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    top_tags = [str(t.hashtag) for t in df.select("hashtag").collect()]
    # extract the counts from dataframe and convert them into array
    tags_count = [p.hashtag_count for p in df.select("hashtag_count").collect()]
    # initialize and send the data through REST API
    url = 'http://localhost:5001/updateData'
    request_data = {'label': str(top_tags), 'data': str(tags_count)}
    response = requests.post(url, data=request_data)
    
# create spark configuration
conf = SparkConf().setMaster("local[2]").setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create the Streaming Context from the above spark context with interval size 2 seconds
ssc = StreamingContext(sc, 3)
# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("localhost",9999)
print("datastream")
#dataStream.pprint()
#dataStream.saveAsTextFiles('MS/LSA/Project/Test/test123')
## split each tweet into words
words = dataStream.flatMap(lambda line: line.split("\n"))
#words.saveAsTextFiles('MS/LSA/Project/Test/test123')
#words.foreachRDD(process_string)
## filter the words to get only hashtags, then map each hashtag to be a pair of (hashtag,1)
hashtags = words.map(lambda x: (x, 1))
#hashtags.pprint()
## adding the count of each hashtag to its last count
tags_totals = hashtags.updateStateByKey(aggregate_tags_count)
#tags_totals.pprint()
## do processing for each RDD generated in each interval
print('before rdd')
tags_totals.foreachRDD(process_rdd)
print('after rdd')
# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
