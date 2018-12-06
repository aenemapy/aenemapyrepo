# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,xbmcaddon,os,urlparse,random,json


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

tmdb = params.get('tmdb')

site = params.get('site')

iconimage = params.get('iconimage')

mode = params.get('mode')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

query = params.get('query')

source = params.get('source')

content = params.get('content')
direct = params.get('direct')
provider = params.get('provider')




#------------------------ FREEDOC -----------------------------
if action == 'rdUser':
	
	import tvresolver
	from tvresolver.modules import control
	tvresolver.getDebridUser()
	control.openSettings('1.0')	


	
xbmcplugin.endOfDirectory(int(sys.argv[1]))

