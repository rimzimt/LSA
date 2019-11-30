#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 15:31:44 2019

@author: rimzimthube
"""

'''
Command used in terminal:
python MS/LSA/Project/Working3/WebSiteProducer.py


'''

import socket
import sys
import requests
import requests_oauthlib
import json
from textblob import TextBlob
import csv

fileName= '/Users/rimzimthube/MS/LSA/Project/SavedCSV.csv'

# Replace the values below with yours
access_token = '1189013439777144834-gHdx56y8wdFEXx6on8RvqKFd7jZWgr'
access_secret = 'Xr8IgYAZwbcwOuKOkCogcahAjpZPGz1zOzcEO27cbCqr2'
consumer_key = 'LSrCCGTL3XXvVxUaeMJ1P9kvQ'
consumer_secret = 'dVvm1uFcePm0o0M6fxJg3vxqouoB3o0HOOWlzwhElleH1dOpGj'
my_auth = requests_oauthlib.OAuth1(consumer_key, consumer_secret, \
        access_token, access_secret)

def GetTweetSentiment(tweet_text):
    analysis = TextBlob(tweet_text)
    print(analysis.sentiment)
    if analysis.sentiment[0]>0:
        sentiment='Positive'
    elif analysis.sentiment[0]<0:
        sentiment='Negative'
    else:
        sentiment='Neutral'

    # with open(fileName, 'a') as csvfile:
    # # creating a csv writer object
        # csvwriter = csv.writer(csvfile)
    # # writing the fields
        # csvwriter.writerow([sentiment,tweet_text])
    return sentiment

def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    # query_data = [('language', 'en'), ('tweet_mode','extended'), \
            # ('locations', '-130,-20,100,50'),('track','trump')]
    query_data = [('language', 'en'), ('tweet_mode','extended'), \
            ('track','PriyankaReddy')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + \
        str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response

def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            if 'truncated' not in full_tweet.keys():
                print(full_tweet.keys())
                continue
            extended=full_tweet['truncated']

            #More than 140 chars
            if(extended==True):
                if 'retweeted_status' in full_tweet: #retweet
                    print('1111')
                    # print(full_tweet['text'])
                    # print(full_tweet['retweeted_status']\
                            # ['extended_tweet']['full_text'])
                    # print(json.dumps(full_tweet, indent=4, sort_keys=True))
                    tweet_text=full_tweet['retweeted_status']\
                            ['extended_tweet']['full_text']

                else: #Normal Tweet
                    # print('2222')
                    # print(full_tweet['text'])
                    # print(full_tweet['extended_tweet']['full_text'])
                    tweet_text=full_tweet['extended_tweet']['full_text']
            #140 chars
            elif (extended==False):
                #If normal tweet is RT
                if 'retweeted_status' in full_tweet:
                    if(full_tweet['retweeted_status']['truncated']==True):
                        # print('5555')
                        # print(full_tweet['retweeted_status']\
                                # ['extended_tweet']['full_text'])
                        tweet_text=full_tweet['retweeted_status']['extended_tweet']['full_text']
                    else:
                        # print('3333')
                        # print(full_tweet['text'])
                        # print(full_tweet['retweeted_status']['text'])
                        tweet_text=full_tweet['retweeted_status']['text']
                        # print(json.dumps(full_tweet, indent=4, sort_keys=True))
                else:
                    # print('4444')
                    # print(full_tweet['text'])
                    tweet_text=full_tweet['text']
                # print(json.dumps(full_tweet, indent=4, sort_keys=True))
            # print("Tweet Text: " + tweet_text)
            # print ("------------------------------------------")
            sentiment=GetTweetSentiment(tweet_text)
            tcp_connection.send((sentiment+'\n').encode())
            print("Tweet Sent!")
        except(ConnectionResetError, BrokenPipeError):
            print("Client disconnected ..")
            return
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

def main():
    TCP_IP = "localhost"
    TCP_PORT = 9999
    conn = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    while True:
        s.listen(1)
        print("Waiting for TCP connection...")
        conn, addr = s.accept()
        print("Connected... Starting getting tweets.")
        # print(conn)
        resp = get_tweets()
        send_tweets_to_spark(resp, conn)

if __name__ == '__main__':
    main()
