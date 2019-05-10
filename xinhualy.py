# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 11:13:26 2019

@author: S80240
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from bs4 import BeautifulSoup

import hashlib
import pprint
import random
import requests
import time

_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml'
    }
_SESSION = requests.Session()
_ENCODING='utf-8'

def _get_page(pagerequest):
    """Return the data for a page on telemetro.com"""
    # Note that we include a sleep to avoid overloading the scholar server
    time.sleep(2+random.uniform(0, 6))
    _GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
    _COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
    resp_url = requests.get(pagerequest)
    if resp_url.status_code == 200:
        return resp_url.text
    else:
        raise Exception('Error: {0} {1}'.format(resp_url.status_code, resp_url.reason))
        
def _get_soup(pagerequest):
    """Return the BeautifulSoup for a page"""
    html = _get_page(pagerequest)
    return BeautifulSoup(html, 'lxml')

def _search_in_soup(soup):
    """Generator that returns Publication objects from the search page"""
    return Publication(soup)
        
def search_pubs_url(url):
    """Search by scholar query and return a generator of Publication objects"""
    #url='http://spanish.xinhuanet.com/2015-08/07/c_134489495.htm'
    soup = _get_soup(url)
    return _search_in_soup(soup)

def _body_in_image_soup(soup,body):
    next_soup = _get_soup(soup.findAll("a",{"class": 'nextpage'})[-1]['href'])
    for domPC in next_soup.findAll("div", {"class": 'domPC'}):
            for row in domPC.findAll('p'):
                if not row.find('a'):
                    body = body +" <br>"+ row.text
    #next_soup.findAll("a",{"class": 'nextpage'})                    
    if next_soup.find("img",{"src": lambda L: L and L.endswith('xia.gif')}):
            body = _body_in_image_soup(next_soup,body)
            
    return body

def _body_in_soup(soup):
    """Generator that returns Publication objects from the search page"""
    
    summary = soup.find("meta", {"name": 'description'})['content']
    body= ""
    #soup.findAll('p')
    
    for domPC in soup.findAll("div", {"class": 'domPC'}):
        for row in domPC.findAll('p'):
            if not row.find('a'):
                if summary =="":
                    summary=row.text
                body = body +" <br>"+ row.text
    if soup.find("a",{"class": 'nextpage'}):
        body = _body_in_image_soup(soup,body)
    
    return summary,body
        
def clean_bad_chars(text):
    bad_chars=['\r','\n']
    for bad_char in bad_chars:
        text=text.replace(bad_char,'')
    return text
        
class Publication(object):
    """Returns an object for a single publication"""
    def __init__(self, __data):
        self.bib = dict()
        self.bib['title'] = clean_bad_chars(__data.find("h1").text)
        if __data.find("meta",{"name": 'section'}):
            self.bib['section'] = __data.find("meta",{"name": 'section'})['content']
        else:
            self.bib['section']=''
        if __data.find("meta",{"name": 'pubdate'}):
            self.bib['date'] = clean_bad_chars(__data.find("meta",{"name": 'pubdate'})['content'])
        else:
            self.bib['date']=''
        
        summary,body=_body_in_soup(__data)
        
        self.bib['summary']=clean_bad_chars(summary)
        self.bib['body']=clean_bad_chars(body)
                
    def __str__(self):
        return pprint.pformat(self.__dict__)
    
    
    
#############################33
        
    
import codecs, json
import pandas as pd
from tqdm import tqdm            
import requests

main_path='C:\\Users\\S80240\\Desktop\\Everis\\IA\\scrapping\\Twitter\\'
tweet_files=[
'tweets-2015.json',
'tweets-2016.json',
'tweets-2017.json',
'tweets-2018.json',
'tweets-2019-04-15.json'
]

def unshorten_url(session, url):
    #time.sleep(2+random.uniform(0, 6))
    resp_url=url
    try:
        resp = session.head(url, allow_redirects=True)
        resp_url=resp.url
    except Exception as e:
        print(e)
        print(url)
    
    return resp_url
    

session = requests.Session()
for tweet_file in tweet_files:
    links=[]
    with codecs.open(main_path+tweet_file, 'r', 'utf-8') as f:
        tweets = json.load(f, encoding='utf-8')
        
    list_tweets = [list(elem.values()) for elem in tweets]
    list_columns = list(tweets[0].keys())
    tweets_df = pd.DataFrame(list_tweets, columns=list_columns)
    
    for index, tweet in tqdm(tweets_df.iterrows()):
        text = tweet['text'].replace('\n',' ').replace(u'\xa0', u' ')
        text_list = text.split(' ')
        for word in text_list:
            if 'xhne.ws' in word:
                index = word.find('http')
                link = unshorten_url(session,word[index:index+20])
                if link.find('spanish.xinhuanet.com')>0:
                    links.append(link)
                    len(links)

    for link in tqdm(links):    
        q= search_pubs_url(link)
        
        f= open("..//xinhua_"+tweet_file+".txt","a+")#,errors = 'ignore'        
        try:
            f.write(q.bib['title']+"|"+q.bib['section']+"|"+q.bib['date']+"|"+link+"|"+q.bib['summary']+"|"+q.bib['body']+"\n")
        except: 
            f_e= open("..//xinhua_"+tweet_file+"_exception.txt","a+")
            f_e.write(q.bib['title']+"|"+q.bib['section']+"|"+q.bib['date']+"|"+link+"\n")
            f_e.close()
        f.close()         