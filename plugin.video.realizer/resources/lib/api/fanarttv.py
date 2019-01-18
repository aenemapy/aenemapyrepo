# -*- coding: utf-8 -*-

from resources.lib.modules import control
from resources.lib.modules import client
import requests
import os,sys,re,json,urllib,urlparse,base64,datetime,time,json
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
ftvAPI = control.setting('fanart.tv.project')
ApiTv = 'http://webservice.fanart.tv/v3/tv/%s?api_key=%s' % ("%s", ftvAPI)
ApiMovies = 'http://webservice.fanart.tv/v3/movies/%s?api_key=%s' % ("%s", ftvAPI)	

def get(imdb, query):
	if query == 'movies':  art = ApiMovies % imdb
	else: art = ApiTv % imdb
	art = requests.get(art).json()

#	########### MOVIES ########################
	if query == 'movies': 
		try:
			poster = art['movieposter']
			poster = [(x['url'],x['likes']) for x in poster if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in poster if x.get('lang') == '00']
			poster = [(x[0],x[1]) for x in poster]
			poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)	
			poster = [x[0] for x in poster][0]
			poster = poster.encode('utf-8')
			
		except: poster = '0'
		if not 'http' in poster: poster = '0'
	
		try:
			fanart = art['moviebackground']
			fanart = [(x['url'],x['likes']) for x in fanart]
			fanart = [(x[0],x[1]) for x in fanart]
			fanart = sorted(fanart, key = lambda x : int(x[1]), reverse= True)	
			fanart = [x[0] for x in fanart][0]
			fanart = fanart.encode('utf-8')
			
		except: fanart = '0'
		if not 'http' in fanart: fanart = '0'
		
		try:
			banner = art['moviebanner']
			banner = [(x['url'],x['likes']) for x in banner if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in banner if x.get('lang') == '00']
			banner = [(x[0],x[1]) for x in banner]
			banner = sorted(banner, key = lambda x : int(x[1]), reverse= True)	
			banner = [x[0] for x in banner][0]
			banner = banner.encode('utf-8')
			
		except: banner = '0'
		if not 'http' in banner: banner = '0'		
		
		
	else: 
		try:
			poster = art['tvposter']
			poster = [(x['url'],x['likes']) for x in poster if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in poster if x.get('lang') == '00']
			poster = [(x[0],x[1]) for x in poster]
			poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)	
			poster = [x[0] for x in poster][0]
			poster = poster.encode('utf-8')
			
		except: poster = '0'
		if not 'http' in poster: poster = '0'
	
		try:
			fanart = art['showbackground']
			fanart = [(x['url'],x['likes']) for x in fanart]
			fanart = [(x[0],x[1]) for x in fanart]
			fanart = sorted(fanart, key = lambda x : int(x[1]), reverse= True)	
			fanart = [x[0] for x in fanart][0]
			fanart = fanart.encode('utf-8')
			
		except: fanart = '0'
		if not 'http' in fanart: fanart = '0'
		
		try:
			banner = art['tvbanner']
			banner = [(x['url'],x['likes']) for x in banner if x.get('lang') == 'en'] + [(x['url'],x['likes']) for x in banner if x.get('lang') == '00']
			banner = [(x[0],x[1]) for x in banner]
			banner = sorted(banner, key = lambda x : int(x[1]), reverse= True)	
			banner = [x[0] for x in banner][0]
			banner = banner.encode('utf-8')
			
		except: banner = '0'
		if not 'http' in banner: banner = '0'
	
	meta = {'poster':poster, 'fanart':fanart, 'banner':banner}
	# print ("FANART TV meta", meta)	
	return meta


	
