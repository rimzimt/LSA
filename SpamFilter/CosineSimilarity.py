#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 17:14:48 2019

@author: rimzimthube
"""

from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import textract
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

#nltk.download('punkt')

def readFile(filename):
    with open(filename, 'r') as file:
        doc = file.read()
        
    return doc
    
def processData(doc):
    
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(doc) 
    
    wordsFiltered=[]
    for w in word_tokens:
        if w not in stop_words:
            wordsFiltered.append(w)
        
    ps = PorterStemmer()
 
    wordsStemmed=[]
    for word in wordsFiltered:
        wordsStemmed.append(ps.stem(word))
                
    wordsStemmed=' '.join(wordsStemmed)
    
#    print(wordsStemmed)
        
    return wordsStemmed

doc1=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc1.txt'))
doc2=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc2.txt'))
doc3=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc3.txt'))
doc4=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc4.txt'))
doc5=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc5.txt'))
doc6=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/doc6.txt'))
spam=processData(readFile('/Users/rimzimthube/MS/LSA/HW/VectorSpaceModel/SpamDictionary.txt'))



docs=[doc1,doc2,doc3,doc4,doc5,doc6,spam]

temp={'invest': 0,'free': 1, 'click':2,'visit':3,'open':4, 'attach':5,'call':6,'number':7,
              'money': 8,'out': 9,'extra': 10,'offer': 11,'avail': 12, 
              'pension': 13, 'opportun': 14, 'chanc': 15}

#Dict = dict([('free', 1), ('click',1),('visit',1),('open',1),('attach',1),('call',1),('number',1),
#              ('money', 1),('out', 1),('extra', 1),('offer', 1),('avail', 1), 
#              ('pension', 2), ('opportun', 1), ('chanc', 1),('invest', 1) ])

vector=TfidfVectorizer(vocabulary=temp,stop_words='english')
docSparseMatrix=vector.fit_transform(docs)
docDenseMatrix=docSparseMatrix.todense()

df = pd.DataFrame(docDenseMatrix, 
                  columns=vector.get_feature_names(), 
                  )

print(df)
print(cosine_similarity(df, df))
#




