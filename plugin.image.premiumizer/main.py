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

query = params.get('query')

source = params.get('source')

content = params.get('content')

if action == None:
    from resources.lib.indexers import navigator
    navigator.navigator().root()
	
elif action == 'play':
	from resources.lib.sources import sources	
	sources().play(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, select=select)
	
elif action == 'directPlay':
	from resources.lib.sources import sources	
	sources().directPlay(url, title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, select=select)

		
elif action == 'helpNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().help()

elif action == 'changelogNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().changelog()
	
	
	
# PREMIUMIZE SECTION #################
elif action == 'premiumizeNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().premiumizeNav()
	
elif action == 'premiumizeAdd':
    from resources.lib.api import premiumize
    premiumize.add()
	
elif action == 'premiumizeAdd':
    from resources.lib.api import premiumize
    premiumize.add()

elif action == 'premiumizeTransfers':
    from resources.lib.api import premiumize
    premiumize.transferList()	

elif action == 'premiumizeClearFinished':
    from resources.lib.api import premiumize
    premiumize.clearfinished()	

elif action == 'premiumizerootFolder':
    from resources.lib.api import premiumize
    premiumize.getFolder('root')	

elif action == 'premiumizeOpenFolder':
    from resources.lib.api import premiumize
	
    premiumize.getFolder(id, meta=meta)	
	
elif action == 'premiumizeDeleteItem':
    from resources.lib.api import premiumize
    premiumize.deleteItem(id, type)	

elif action == 'downloadFolder':
    from resources.lib.api import premiumize
    premiumize.downloadFolder(name, id)	
	
elif action == 'premiumizeRename':
    from resources.lib.api import premiumize
    premiumize.renameItem(title, id, type)	


elif action == 'infoCheck':
    from resources.lib.indexers import navigator
    navigator.navigator().infoCheck('')


elif action == 'download':
    from resources.lib.api import premiumize
    premiumize.downloadItem(name, url)

elif action == 'addItem':
    from resources.lib.sources import sources
    sources().addItem(title)

elif action == 'playItem':
   from resources.lib.sources import sources
   sources().playItem(title, source)

elif action == 'backupSettings':
	from resources.lib.modules import updater
	updater.backupAddon()
	
elif action == 'restoreSettings':
	from resources.lib.modules import updater
	updater.restoreAddon()


		
	
	
