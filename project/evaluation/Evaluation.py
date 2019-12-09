#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:51:54 2019

@author: rimzimthube
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 16:31:30 2019

@author: rimzimthube
"""
from textblob import TextBlob
from sklearn.metrics import accuracy_score,confusion_matrix,f1_score,precision_score,recall_score
import re
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords 

'''
Pre process the text 
'''
def processText(text):
    
    _stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])


    tweet = text.lower() # convert text to lower-case
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet) # remove usernames
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag
    tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
    tweet=[word for word in tweet if word not in _stopwords]
    
    tweet=' '.join(tweet)
    return tweet

'''
Build training set from the CSV file
'''
 
def buildTrainSet(corpusFile):
    import csv

    trainingDataSet=[]
    
    with open(corpusFile,'rt') as csvfile:
        lineReader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        for row in lineReader:
            trainingDataSet.append({"tweet_id":row[0], "label":row[2], "topic":row[3],"text":row[1]})
            
    return trainingDataSet


'''
Get sentiment for the text
'''          
def getSentiment(trainSet):
    
    sentimentTweetBlob=[]
    sentimentFile=[]
    
    postiveBlob=0
    negativeBlob=0
    neutralBlob=0
    postiveFile=0
    negativeFile=0
    neutralFile=0

    for tweet in trainSet:
        text=tweet["text"]
        
        text=processText(text)
        
        if(tweet["label"]!='irrelevant'):
            
            sentimentFile.append(tweet["label"])
#            if(tweet["label"]=='positive'):
#                postiveFile=postiveFile+1
#            elif(tweet["label"]=='negative'):
#                negativeFile=negativeFile+1
#            elif(tweet["label"]=='neutral'):
#                neutralFile=neutralFile+1
            
            analysis = TextBlob(text)    
            if analysis.sentiment[0]>0.4:  
                sentimentTweetBlob.append('positive')
            
#                postiveBlob=postiveBlob+1
            elif analysis.sentiment[0]<0:   
                sentimentTweetBlob.append('negative')
                
#                negativeBlob=negativeBlob+1
            else:   
                sentimentTweetBlob.append('neutral')
                
#                neutralBlob=neutralBlob+1
        
    
    accuracy=accuracy_score(sentimentFile,sentimentTweetBlob)
    print('Accuracy - '+format(accuracy))
    
    confusion=confusion_matrix(sentimentFile,sentimentTweetBlob,labels=["positive", "negative", "neutral"])
    print('Confusion matrix - \n'+format(confusion))
    
    f1score=f1_score(sentimentFile, sentimentTweetBlob,labels=["positive", "negative", "neutral"],average='macro')
    print('F1 score - '+format(f1score))
    
    precisionScore=precision_score(sentimentFile, sentimentTweetBlob, average='macro')
    print('Precision Value - '+format(precisionScore))
    
    recall= recall_score(sentimentFile, sentimentTweetBlob, average='macro')
    print('Recall - '+format(recall))
            
#    print('postiveBlob - '+format(postiveBlob))
#    print('negativeBlob - '+format(negativeBlob))
#    print('neutralBlob - '+format(neutralBlob))
#    print('total - '+format(neutralBlob+postiveBlob+negativeBlob))
#    print('postiveFile - '+format(postiveFile))
#    print('negativeFile - '+format(negativeFile))
#    print('neutralFile - '+format(neutralFile))
#    print('total - '+format(postiveFile+negativeFile+neutralFile))


corpusFile = "/home/ubuntu/LSA/project/evaluation/downloadedCorpus.csv"

trainSet=buildTrainSet(corpusFile)

getSentiment(trainSet)



