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
import argparse
from textblob import TextBlob
import csv
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 
from string import punctuation 
from pymongo import MongoClient
import datetime
import nltk


twitterdb=None
tweetCollection=None
fileName= '/Users/rimzimthube/MS/LSA/Project/SavedCSV.csv'
trend_var = ''

# Replace the values below with yours
access_token = '1189013439777144834-gHdx56y8wdFEXx6on8RvqKFd7jZWgr'
access_secret = 'Xr8IgYAZwbcwOuKOkCogcahAjpZPGz1zOzcEO27cbCqr2'
consumer_key = 'LSrCCGTL3XXvVxUaeMJ1P9kvQ'
consumer_secret = 'dVvm1uFcePm0o0M6fxJg3vxqouoB3o0HOOWlzwhElleH1dOpGj'
mongoclient = MongoClient('mongodb+srv://rimzimt:Rimzim!123@cluster0-x8z3i.mongodb.net/test?retryWrites=true&w=majority')
my_auth = requests_oauthlib.OAuth1(consumer_key, consumer_secret,access_token, access_secret)

def processText(text):
    _stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])
    emoji_pattern = re.compile("["
         u"\U0001F600-\U0001F64F"  # emoticons
         u"\U0001F300-\U0001F5FF"  # symbols & pictographs
         u"\U0001F680-\U0001F6FF"  # transport & map symbols
         u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
         u"\U00002702-\U000027B0"
         u"\U000024C2-\U0001F251"
         "]+", flags=re.UNICODE)

    emoticons_happy = set([
    ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3'
    ])

    emoticons_sad = set([
    ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';('
    ])

    emoticons = emoticons_happy.union(emoticons_sad)

    tweet = text.lower() # convert text to lower-case
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag

    tweet = re.sub(r':', '', tweet) # preprocessing the colon symbol left remain after 
    tweet = re.sub(r'‚Ä¶', '', tweet) #removing mentions
    tweet = re.sub(r'[^\x00-\x7F]+',' ', tweet) ##replace consecutive non-ASCII characters with a space
    tweet = emoji_pattern.sub(r'', tweet)

    tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
    tweet=[word for word in tweet if word not in _stopwords and word not in emoticons]

    tweet=' '.join(tweet)
    return tweet

def GetTweetSentiment(tweet_text):
    tweet_text = processText(tweet_text)
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
    global trend_var
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    # query_data = [('language', 'en'), ('tweet_mode','extended'), \
            # ('locations', '-130,-20,100,50'),('track','trump')]
    query_data = [('language', 'en'), ('tweet_mode','extended'), \
            ('track', trend_var)]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + \
        str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response

def send_tweets_to_spark(http_resp, tcp_connection):
    global tweetCollection
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
            mongoTweet={'tweet':tweet_text,'sentiment':sentiment,'hashtag':trend_var,'DateTime':datetime.datetime.now()}
            tweetCollection.insert_one(mongoTweet)
            tcp_connection.send((sentiment+'\n').encode())
            print("Tweet Sent!")
        except (LookupError, NameError):
            e = sys.exc_info()[0]
            print(tweet_text)
            print("Error: %s" % e)
            exit(0)
        except(ConnectionResetError, BrokenPipeError):
            print("Client disconnected ..")
            return
        except(json.decoder.JSONDecodeError):
            continue
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)


def argsStuff():
    parser = argparse.ArgumentParser(description = "Twitter sentiment analysis")
    parser.add_argument("-V", "--version", help="show program version", \
            action="store_true")
    parser.add_argument("-w", "--word", help="hashtag for sentiment analysis",\
            type=str)
    args = parser.parse_args()
    if args.version:
        print("V1.1")
        exit(0)
    if not args.word:
        print("The following arguments are required: -w/--word")
        exit(1)
    return args.word

def main():
    global trend_var
    global tweetCollection
    global twitterdb
    # nltk.download('stopwords')
    trend_var = argsStuff()
    print(trend_var)
    TCP_IP = "localhost"
    TCP_PORT = 9999
    twitterdb=mongoclient['twitterdb']
    tweetCollection=twitterdb['tweetcollection']

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
