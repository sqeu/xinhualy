# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 14:12:23 2019

@author: S80240
"""

"""
Scrapped using twitterscraper with the command:
twitterscraper "xhne.ws from:XHespanol" -bd 2014-01-01 -ed 2014-12-31 -o tweets-2014.json

Tweets	Year
1886	2019/01/01 - 2019/04/15
7957	2018
6953	2017
6848	2016
2534	2015

Total = 26178
"""
import twitterscraper

#Or save the retrieved tweets to file:
file = open('output.txt','w',errors = 'ignore')
for tweet in twitterscraper.query.query_tweets_from_user('XHespanol'):
    file.write(tweet)
file.close()

"""
Reading the tweets
"""
import codecs, json
import pandas as pd
from tqdm import tqdm            


main_path='C:\\Users\\S80240\\Desktop\\Everis\\IA\\scrapping\\Twitter\\'
tweet_files=[
'tweets-2015.json',
'tweets-2016.json',
'tweets-2017.json',
'tweets-2018.json',
'tweets-2019-04-15.json'
]

import xinhualy

for tweet_file in tweet_files:
    links=[]
    with codecs.open(main_path+tweet_file, 'r', 'utf-8') as f:
        tweets = json.load(f, encoding='utf-8')
        
    list_tweets = [list(elem.values()) for elem in tweets]
    list_columns = list(tweets[0].keys())
    tweets_df = pd.DataFrame(list_tweets, columns=list_columns)
    
    for index, tweet in tweets_df.iterrows():
        text = tweet['text'].replace('\n',' ').replace(u'\xa0', u' ')
        text_list = text.split(' ')
        for word in text_list:
            if 'xhne.ws' in word:
                index = word.find('http')
                links.append(word[index:20])
            
    for link in links:
        
        search_query= xinhualy.search_pubs_url(link)
        
        f= open("..//xinhua_"+tweet_file+".txt","a+")#,errors = 'ignore'
        for q in tqdm(search_query):
            try:
                f.write(q.bib['title']+"|"+q.bib['kicker']+"|"+q.bib['date']+"|"+q.bib['link']+"|"+q.bib['summary']+"|"+q.bib['body']+"\n")
            except: 
                f_e= open("..//xinhua_"+tweet_file+"_exception.txt","a+")
                f_e.write(q.bib['title']+"|"+q.bib['kicker']+"|"+q.bib['date']+"|"+q.bib['link']+"\n")
                f_e.close()
        f.close()
        

     
