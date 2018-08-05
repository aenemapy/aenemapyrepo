# -*- coding: utf-8 -*-

from urlparse import parse_qsl
import sys
params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

icon = params.get('icon')

id = params.get('id')

type = params.get('type')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

tmdb = params.get('tmdb')

season = params.get('season')

episode = params.get('episode')

tvshowtitle = params.get('tvshowtitle')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

offset = params.get('offset')

source = params.get('source')

content = params.get('content')


if action == None:

    from resources.lib.indexers import navigator
    navigator.navigator().root()

elif action == 'most_populars':
	from resources.lib.api import aptoide	
	aptoide.getPopulars(offset=offset)
	
	
elif action == 'AppSelect':
	from resources.lib.api import aptoide	
	aptoide.AppSelect(title, id)	
	
elif action == 'searchApp':
	from resources.lib.api import aptoide	
	aptoide.searchApp()		
	
elif action == 'getGames':
	from resources.lib.api import aptoide	
	aptoide.getGames()	

elif action == 'getApplications':
	from resources.lib.api import aptoide	
	aptoide.getApplications()			
	
elif action == 'getStore':
	from resources.lib.api import aptoide	
	aptoide.getStore(id)	
	
	
	
