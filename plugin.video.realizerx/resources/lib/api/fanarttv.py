# -*- coding: utf-8 -*-

from resources.lib.modules import control, cache
from resources.lib.modules import client
import urllib.parse as urlparse
import requests
import os,sys,re,json,urllib.request,urllib.parse,urllib.error,base64,datetime,time,json
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
ftvAPI = control.setting('fanart.tv.project')
if ftvAPI == '' or ftvAPI == None: ftvAPI = 'c0f8fe09b047737777e4cb525105ab94'
ApiTv = 'http://webservice.fanart.tv/v3/tv/%s?api_key=%s' % ("%s", ftvAPI)
ApiMovies = 'http://webservice.fanart.tv/v3/movies/%s?api_key=%s' % ("%s", ftvAPI)  

def get(imdb, query):
    meta = cache.get(getmeta, 720, imdb, query)
    return meta
    
def getmeta(imdb, query):
    if query == 'movies':  art = ApiMovies % imdb
    else: art = ApiTv % imdb
    art = requests.get(art).json()

#   ########### MOVIES ########################
    if query == 'movies': 
        try:
            poster = art['movieposter']
            poster = [(x['url'],x['likes']) for x in poster if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in poster if x.get('lang') == '00']
            poster = [(x[0],x[1]) for x in poster]
            poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)  
            poster = [x[0] for x in poster][0]
            poster = poster
            
        except: poster = '0'
        if not 'http' in poster: poster = '0'
        try:
            fanart = art['moviebackground']
            fanart = [(x['url'],x['likes']) for x in fanart]
            fanart = [(x[0],x[1]) for x in fanart]
            fanart = sorted(fanart, key = lambda x : int(x[1]), reverse= True)  
            fanart = [x[0] for x in fanart][0]
            fanart = fanart
            
        except: fanart = '0'
        if not 'http' in fanart: fanart = '0'
        try:
            banner = art['moviebanner']
            banner = [(x['url'],x['likes']) for x in banner if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in banner if x.get('lang') == '00']
            banner = [(x[0],x[1]) for x in banner]
            banner = sorted(banner, key = lambda x : int(x[1]), reverse= True)  
            banner = [x[0] for x in banner][0]
            banner = banner
            
        except: banner = '0'
        if not 'http' in banner: banner = '0'
        try:
            clearlogo = art['hdmovielogo']
            clearlogo = [(x['url'],x['likes']) for x in clearlogo if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in clearlogo if x.get('lang') == '00']
            clearlogo = [(x[0],x[1]) for x in clearlogo]
            clearlogo = sorted(clearlogo, key = lambda x : int(x[1]), reverse= True)    
            clearlogo = [x[0] for x in clearlogo][0]
            clearlogo = clearlogo
            
        except: clearlogo = '0'
        if not 'http' in clearlogo: clearlogo = '0'
    
        try:
            discart = art['moviedisc']
            discart = [(x['url'],x['likes']) for x in discart if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in discart if x.get('lang') == '00']
            discart = [(x[0],x[1]) for x in discart]
            discart = sorted(discart, key = lambda x : int(x[1]), reverse= True)    
            discart = [x[0] for x in discart][0]
            discart = discart
            
        except: discart = '0'
        if not 'http' in discart: discart = '0' 
        
        try:
            clearart = art['hdmovieclearart']
            clearart = [(x['url'],x['likes']) for x in clearart if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in clearart if x.get('lang') == '00']
            clearart = [(x[0],x[1]) for x in clearart]
            clearart = sorted(clearart, key = lambda x : int(x[1]), reverse= True)  
            clearart = [x[0] for x in clearart][0]
            clearart = clearart
            
        except: clearart = '0'
        if not 'http' in clearart: clearart = '0'           
    

    else: 
        try:
            poster = art['tvposter']
            poster = [(x['url'],x['likes']) for x in poster if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in poster if x.get('lang') == '00']
            poster = [(x[0],x[1]) for x in poster]
            poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)  
            poster = [x[0] for x in poster][0]
            poster = poster
            
        except: poster = '0'
        if not 'http' in poster: poster = '0'
    
        try:
            fanart = art['showbackground']
            fanart = [(x['url'],x['likes']) for x in fanart]
            fanart = [(x[0],x[1]) for x in fanart]
            fanart = sorted(fanart, key = lambda x : int(x[1]), reverse= True)  
            fanart = [x[0] for x in fanart][0]
            fanart = fanart
            
        except: fanart = '0'
        if not 'http' in fanart: fanart = '0'
        
        try:
            banner = art['tvbanner']
            banner = [(x['url'],x['likes']) for x in banner if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in banner if x.get('lang') == '00']
            banner = [(x[0],x[1]) for x in banner]
            banner = sorted(banner, key = lambda x : int(x[1]), reverse= True)  
            banner = [x[0] for x in banner][0]
            banner = banner
            
        except: banner = '0'
        if not 'http' in banner: banner = '0'
        
        try:
            clearlogo = art['hdtvlogo']
            clearlogo = [(x['url'],x['likes']) for x in clearlogo if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in clearlogo if x.get('lang') == '00']
            clearlogo = [(x[0],x[1]) for x in clearlogo]
            clearlogo = sorted(clearlogo, key = lambda x : int(x[1]), reverse= True)    
            clearlogo = [x[0] for x in clearlogo][0]
            clearlogo = clearlogo
            
        except: clearlogo = '0'
        if not 'http' in clearlogo: clearlogo = '0'
        
        try:
            clearart = art['clearart']
            clearart = [(x['url'],x['likes']) for x in clearart if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in clearart if x.get('lang') == '00']
            clearart = [(x[0],x[1]) for x in clearart]
            clearart = sorted(clearart, key = lambda x : int(x[1]), reverse= True)  
            clearart = [x[0] for x in clearart][0]
            clearart = clearart
            
        except: clearart = '0'
        if not 'http' in clearart: clearart = '0'
        
        discart = '0'
    
    meta = {'poster':poster, 'fanart':fanart, 'banner':banner, 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart}
    return meta
