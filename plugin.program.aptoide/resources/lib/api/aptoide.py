from resources.lib.modules import control, cleantitle
import requests
import os,sys,re,json,urllib,urlparse,json
import xbmc, xbmcaddon, xbmcgui, xbmcvfs

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

addonInfo = xbmcaddon.Addon().getAddonInfo
profilePath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')

aptoide_API = 'https://ws75.aptoide.com/api/7'
appMeta = '/app/getMeta/app_id='
popular_apps = '/apps/get/sort=downloads/limit=100/offset='
group_apps = '/apps/get/limit=100/sort=downloads/group_name='


icon = control.icon
fanart = control.fanart

def getPopulars(offset=None):
    if offset == None: offset = '0'
    link = popular_apps + offset
    url = aptoide_API + link
    r = requests.get(url).json()
    r = r['datalist']['list']
    for item in r:
		name = item['name'].encode('utf-8')
		name = cleantitle.normalize(name)
		id = item['id']
		downloads = item['stats']['downloads']
		icon = item['icon']
		fanart = item['graphic']
		version = item['file']['vername'].encode('utf-8')
		label = name + " [" + version + "]"
		item = control.item(label=label)
		isFolder = False
		item.setArt({'icon': icon, 'thumb': icon})
		if fanart == '' or fanart == None: fanart = control.fanart
		item.setProperty('Fanart_Image', fanart)
		description = 'DOWNLOADS: ' + str(downloads)
		meta = {'plot': description}
		meta.update({'Title': label})
		sysname = cleantitle.geturl(name)
		item.setInfo( type="Video", infoLabels= meta )
		url = '%s?action=%s&id=%s&title=%s' % (sysaddon, 'AppSelect', id, sysname)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
    control.directory(syshandle, cacheToDisc=False)	

def AppSelect(title, id):

	type = ['Download App', 'Install App']
	select = control.selectDialog(type)
	if select == 0: downloadApp(title, id)
	elif select == 1: installApp(title, id)
	else: return

def downloadApp(title, id):
	
	link = appMeta + id
	url = aptoide_API + link
	r = requests.get(url).json()
	path = r['data']['file']['path']
	title = title + ".apk"
	from resources.lib.modules import downloader
	loc = control.setting('download.path')
	downloader.downloadAPK(title, path)
	
	
def installApp(title, id):
	link = appMeta + id
	url = aptoide_API + link
	r = requests.get(url).json()
	path = r['data']['file']['path']
	title = title + ".apk"
	from resources.lib.modules import downloader
	loc = control.setting('download.path')
	downloader.installAPK(title, path)
	
def searchApp():

	k = control.keyboard('', 'Search APP') ; k.doModal()	
	q = k.getText() if k.isConfirmed() else None

	if (q == None or q == ''): return
	query = '/apps/search/query=%s/limit=50' % q
	url = aptoide_API + query
	getAppsUrl(url)
	
	
def getAppsUrl(url):
    r = requests.get(url).json()
    r = r['datalist']['list']
    for item in r:
		name = item['name'].encode('utf-8')
		name = cleantitle.normalize(name)
		id = item['id']
		downloads = item['stats']['downloads']
		icon = item['icon']
		fanart = item['graphic']
		version = item['file']['vername'].encode('utf-8')
		label = name + " [" + version + "]"
		item = control.item(label=label)
		isFolder = False
		item.setArt({'icon': icon, 'thumb': icon})
		if fanart == '' or fanart == None: fanart = control.fanart
		item.setProperty('Fanart_Image', fanart)
		description = 'DOWNLOADS: ' + str(downloads)
		meta = {'plot': description}
		meta.update({'Title': label})
		sysname = cleantitle.geturl(name)
		item.setInfo( type="Video", infoLabels= meta )
		url = '%s?action=%s&id=%s&title=%s' % (sysaddon, 'AppSelect', id, sysname)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    control.directory(syshandle, cacheToDisc=False)	
	
	
def getStore(name):
    link = group_apps + name
    url = aptoide_API + link
    r = requests.get(url).json()
    r = r['datalist']['list']
    for item in r:
		name = item['name'].encode('utf-8')
		name = cleantitle.normalize(name)
		id = item['id']
		downloads = item['stats']['downloads']
		icon = item['icon']
		fanart = item['graphic']
		if fanart == '' or fanart == None: fanart = control.fanart
		version = item['file']['vername'].encode('utf-8')
		label = name + " [" + version + "]"
		item = control.item(label=label)
		isFolder = False
		item.setArt({'icon': icon, 'thumb': icon})
		item.setProperty('Fanart_Image', fanart)
		description = 'DOWNLOADS: ' + str(downloads)
		meta = {'plot': description}
		meta.update({'Title': label})
		item.setInfo( type="Video", infoLabels= meta )
		sysname = cleantitle.geturl(name)
		url = '%s?action=%s&id=%s&title=%s' % (sysaddon, 'AppSelect', id, sysname)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    control.directory(syshandle, cacheToDisc=False)	
		
		
def getGames(offset=None):
    if offset == None: offset = '0'
    link = '/store/groups/get/store_name=apps/group_name=games'
    url = aptoide_API + link
    r = requests.get(url).json()
    r = r['datalist']['list']
    for item in r:
		name = item['name'].encode('utf-8')
		id = item['id']
		id = str(id)

		label = name
		item = control.item(label=label)
		isFolder = True
		item.setArt({'icon': icon, 'thumb': icon})
		item.setProperty('Fanart_Image', fanart)
		url = '%s?action=%s&id=%s' % (sysaddon, 'getStore', name)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
    control.directory(syshandle, cacheToDisc=False)

def getApplications(offset=None):
    if offset == None: offset = '0'
    link = '/store/groups/get/store_name=apps/group_name=applications'
    url = aptoide_API + link
    r = requests.get(url).json()
    r = r['datalist']['list']
    for item in r:
		name = item['name'].encode('utf-8')
		id = item['id']
		id = str(id)

		label = name
		item = control.item(label=label)
		isFolder = True
		item.setArt({'icon': icon, 'thumb': icon})
		item.setProperty('Fanart_Image', fanart)
		url = '%s?action=%s&id=%s' % (sysaddon, 'getStore', name)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
    control.directory(syshandle, cacheToDisc=False)

