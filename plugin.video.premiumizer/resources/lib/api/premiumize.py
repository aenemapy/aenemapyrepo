# -*- coding: utf-8 -*-
from resources.lib.modules import control, cleantitle, client
import requests
import os,sys,re,json,urllib,urlparse
import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import time
import datetime
from difflib import SequenceMatcher
from resources.lib.modules import cache
from resources.lib.api import trakt	
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

addonInfo     = xbmcaddon.Addon().getAddonInfo
profilePath   = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
pmSettings = xbmc.translatePath(os.path.join(profilePath, 'auth.json'))

if control.setting('premiumize.tls') == 'true': premiumize_Api = 'https://www.premiumize.me'
else: premiumize_Api = 'http://www.premiumize.me'
premiumizeInfo = '/api/account/info'
premiumizeAdd = '/api/transfer/create'
premiumizeTransfer = '/api/transfer/list'
premiumizeClearFinished = '/api/transfer/clearfinished'
premiumizeRootFolder = '/api/folder/list'
premiumizeFolder = '/api/folder/list?id='
premiumizeDeleteItem = '/api/item/delete'
premiumizeRenameItem = '/api/item/rename'
premiumizeItemDetails = '/api/item/details'
OAUTH = premiumize_Api + '/token'		
CLIENTID = '978629017'

USER_AGENT = 'Premiumize Addon for Kodi'
BOUNDARY = 'X-X-X'
data = {}
params = {}

VALID_EXT = ['mkv', 'avi', 'mp4' ,'divx', 'mpeg', 'mov', 'wmv', 'avc', 'mk3d', 'xvid', 'mpg', 'flv', 'aac', 'asf', 'm4a', 'm4v', 'mka', 'ogg', 'oga', 'ogv', 'ogx', '3gp', 'VIVO', 'PVA', 'NUV', 'NSV', 'NSA', 'FLI', 'FLC']

def auth():
		data = {'client_id': CLIENTID, 'response_type': 'device_code'}
		result = requests.post(OAUTH, data=data, timeout=10).json()

		line1 = "1) Visit:[B][COLOR skyblue] %s [/COLOR][/B]"
		line2 = "2) Input Code:[B][COLOR skyblue] %s [/COLOR][/B]"
		line3 = "Note: Your code has been copied to the clipboard"
		verification_url = (line1 % result['verification_uri']).encode('utf-8')
		user_code = (line2 % result['user_code']).encode('utf-8')
		expires_in = result['expires_in']
		device_code = result['device_code']
		interval = result['interval']
		
		try:
			from resources.lib.modules import clipboard
			clipboard.Clipboard.copy(result['user_code'])
		except:pass

		progressDialog = control.progressDialog
		progressDialog.create('Premiumize Auth', verification_url, user_code, line3)

		for i in range(0, int(expires_in)):
			try:
				if progressDialog.iscanceled(): break
				time.sleep(1)
				if not float(i) % interval == 0: raise Exception()

				percent = (i * 100) / int(expires_in)
				progressDialog.update(percent, verification_url, user_code, line3)
				
				r = getAuth(OAUTH , device_code)
				print ("PREMIUMIZE AUTH", r)
				if 'access_token' in str(r): 
					token = r['access_token']
					refresh_token = r['expires_in']				
					control.infoDialog('Premiumize Authorized')	
					control.setSetting(id='premiumize.status', value='Authorized')
					control.setSetting(id='premiumize.token', value=str(token))		
					control.setSetting(id='premiumize.refresh', value=str(refresh_token))							
					try: progressDialog.close()
					except: pass  					
				
					return token
					break
			except:
				pass
				
		try: progressDialog.close()
		except: pass
					
				
def validAccount(): 
		token = getToken()
		if token != '' and token != '0' and token != None: return True
		else: return False
				
def getAuth(url, device_code): 
	data = {'client_id': CLIENTID, 'code': device_code, 'grant_type': 'device_code'}
	result = requests.post(url, data=data, timeout=10).json()
	return result

def saveJson(token=None, refresh_token=None, expires_in=None):
		timeNow = datetime.datetime.now().strftime('%Y%m%d%H%M')
		dirCheck = xbmc.translatePath(profilePath)
		if not os.path.exists(dirCheck): os.makedirs(xbmc.translatePath(dirCheck))
		if token != None: data = {'client_id': CLIENTID, 'token': token, 'refresh_token': refresh_token , 'added':timeNow}
		else: data = {'client_id': CLIENTID, 'token':'0', 'refresh_token': '0' , 'added': timeNow}
		with open(pmSettings, 'w') as outfile: json.dump(data, outfile, indent=2)
		
		
	# REAL DEBRID TOKEN #######################################		
def getToken(refresh=False):
	token = '0'
	token = control.setting('premiumize.token')
	if token == '' or token == None or token =='0': control.infoDialog('Premiumize is not Authorized','Please authorize in the settings')
	else: return token

def reqJson(url, params=None, data=None, multipart_data=None):
    if data == None: data = {}
    token = getToken()
    headers = {'Authorization': 'Bearer %s' % token, 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    if multipart_data != None: 
		headers['Content-Type'] = 'multipart/form-data; boundary=%s' % (BOUNDARY)
		try: result = requests.post(url, data=multipart_data, headers=headers, timeout=30).json()
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)
    else:
		try: result = requests.post(url, params=params, headers=headers, data=data, timeout=30).json()
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)	
		if "bad_token" in result: control.infoDialog('Premiumize is not Authorized', 'Please authorize in the settings')
    return result

		
	
def info():
    label = 'CANNOT GET ACCOUNT INFO'
    url = urlparse.urljoin(premiumize_Api, premiumizeInfo)
    r = reqJson(url)
    status = r['status']
    if status == 'success':
		expire = r['premium_until']

		expirationDate = datetime.datetime.fromtimestamp(expire)
		expirationDate = expirationDate.strftime('%Y-%m-%d')
		
		print ("PREMIUMIZE PREMIUM UNTIL", expire)
		limits = r['limit_used']
		try:
			size   = r['space_used']
			size   = getSize(size)
		except: size = '0'
		numb = str(limits)
		perc = "{:.0%}".format(float(numb))
		label = '[FAIR USE: %s] [CLOUD SIZE: %s] [EXPIRE: %s]'
		label = label % (perc, size, expirationDate)
    else: label = 'CANNOT GET ACCOUNT INFO: '
    return label
	
	
def add():
	type = ['Add with Link', 'Add with File']
	select = control.selectDialog(type)
	if select == 1: add_file()
	elif select == 0: 
		k = control.keyboard('', 'Paste torrent Link') ; k.doModal()	
		q = k.getText() if k.isConfirmed() else None

		if (q == None or q == ''): return
		add_download(q, q)
		
def downloadItem(name, url, id):
	from resources.lib.modules import downloader
	downloader.downloader().download(name, url)
		
def deleteItem(id, type):
	data = {'id': id , 'type': type}
	if type == 'folder': deleteUrl = '/api/folder/delete'
	elif type == 'torrent': deleteUrl = '/api/transfer/delete'
	else: deleteUrl = premiumizeDeleteItem
	url = urlparse.urljoin(premiumize_Api, deleteUrl) 
	r = reqJson(url, data=data)
	control.refresh()
	
def renameItem(title, id, type):
	data = {'id': id , 'type': type}
	if type == 'folder': renameUrl = '/api/folder/rename'
	elif type == 'torrent': renameUrl = '/api/transfer/rename'
	else: renameUrl = premiumizeRenameItem
	folderName = ''
	
	if type != 'folder':
		u = urlparse.urljoin(premiumize_Api, premiumizeItemDetails) 
		details = reqJson(u, data=data)

		filename = details['name']	
		ext = filename.split('.')[-1]
		folderId = details['folder_id']	
		x = premiumizeFolder + str(folderId)
		folder = urlparse.urljoin(premiumize_Api, x)
		folder = reqJson(folder)
		folderName = folder['name']
		if folderName == 'root': folderName = filename
		else: folderName = folderName + '.' + ext
	
	k = control.keyboard(folderName, 'Rename Item (includes Extension)') ; k.doModal()	
	q = k.getText() if k.isConfirmed() else None
	if (q == None or q == ''): return
	data['name'] = q
	url = urlparse.urljoin(premiumize_Api, renameUrl) 
	r = reqJson(url, data=data)
	control.refresh()
	
def libPlayer(title, url, xbmc_id, content):
	from resources.lib.modules import library_player
	library_player.player().run(title, url, xbmc_id, content)
		
		
def getIDLink(id):
	try:

		req = urlparse.urljoin(premiumize_Api, premiumizeItemDetails)
		data = {'id': id}
		result = reqJson(req, data=data)
		if control.setting('transcoded.play') == 'true':
			try:
				playLink = result['stream_link']
				if not "http" in playLink: playLink = result['link']
			except: playLink = result['link']
		else:
			playLink = result['link']

		return playLink
	except: return None

def downloadFolder(name, id):
	data = {'folders[]': id}
	req = urlparse.urljoin(premiumize_Api, '/api/zip/generate')
	u = reqJson(req, data=data)
	print ("DOWNLOAD FOLDER", u)
	zipLink = u['location']
	name = name.replace(' ','_') + ".zip"
	from resources.lib.modules import downloader
	loc = control.setting('download.path')
	dest = os.path.join(loc, name)
	downloader.downloadZip(zipLink, dest, name)
	


def downloadFileToLoc(link, path):
	from resources.lib.modules import downloadzip
	downloadzip.silent_download(link, path)
	

def getFolder(id, meta=None, list=False):
	from resources.lib.indexers import movies, tvshows
	try:
		if id == 'root': url = urlparse.urljoin(premiumize_Api, premiumizeRootFolder) 
		else: 
			folder = premiumizeFolder + id
			url = urlparse.urljoin(premiumize_Api, folder) 
		r = reqJson(url)
		r = r['content']
		lists = []
		for result in r:
			cm = []	
			season = '0'
			isMovie = True
			isFullShow = False
			artMeta = False
			type = result['type']
			fileLabel = type
			id = result['id']
			name = result['name'].encode('utf-8')
			name = normalize(name)
			superInfo = {'title': name, 'year':'0', 'imdb':'0'}
			# RETURN LIST FOR BROWSE SECTION
			if list==True: 
				lists.append(name) 
				continue
			# ##################################
		
			playLink = '0'
			isFolder = True
			isPlayable = 'false'

			url = '%s?action=%s&id=%s' % (sysaddon, 'premiumizeOpenFolder', id)
			
			sysmeta = urllib.quote_plus(json.dumps(superInfo))				
			year = superInfo['year']
			imdb = superInfo['imdb']
			systitle = urllib.quote_plus(superInfo['title'])
			
			links = []
			if type == 'file':
				if control.setting('transcoded.play') == 'true':
					try:
						playLink = result['stream_link']
						if not "http" in playLink: playLink = result['link']
						type = 'TRANSCODED'
					except: playLink = result['link']
				else:
					playLink = result['link']
				playLink = urllib.quote_plus(playLink)
				ext = playLink.split('.')[-1]
				
				if control.setting('filter.files') == 'true':
					if not ext.lower() in VALID_EXT: continue
	
				fileLabel = type + " " + str(ext)
				try: 
					size = result['size']
					size = getSize(size)
				except: size = ''
				if size != '': fileLabel = fileLabel + " | " + str(size)

				isFolder = False
				isPlayable = 'true'

				url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&meta=%s&id=%s' % (sysaddon, 'resolve', systitle , year, imdb, sysmeta, id)
				cm.append(('Queue Item', 'RunPlugin(%s?action=queueItem)' % sysaddon))					
				if control.setting('downloads') == 'true': cm.append(('Download from Cloud', 'RunPlugin(%s?action=download&name=%s&url=%s&id=%s)' % (sysaddon, name, playLink, id)))
			else: cm.append(('Download Folder (Zip)', 'RunPlugin(%s?action=downloadZip&name=%s&id=%s)' % (sysaddon, name, id)))
			
			cm.append(('Delete from Cloud', 'RunPlugin(%s?action=premiumizeDeleteItem&id=%s&type=%s)' % (sysaddon, id, type)))
			cm.append(('Rename Item', 'RunPlugin(%s?action=premiumizeRename&id=%s&type=%s&title=%s)' % (sysaddon, id, type, name)))
			
			if control.setting('file.prefix') == 'true': 			
				label = "[B]" + fileLabel.upper() + " |[/B] " + str(name) 
				
			else: label = str(name)
			
			item = control.item(label=label)
			item.setProperty('IsPlayable', isPlayable)				
			try:
				if ext.lower() == 'mp3' or ext.lower() == 'flac': 
					item.setProperty('IsPlayable', isPlayable)	
					url = playLink
			except:pass
				
			item.setArt({'icon': control.icon, 'thumb': control.icon})
			item.setProperty('Fanart_Image', control.addonFanart())
				
			item.setInfo(type='Video', infoLabels = superInfo)
			item.addContextMenuItems(cm)
			if list != True: control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
			
		if list == True: return lists

		control.directory(syshandle, cacheToDisc=False)
	except: pass

def meta_folder(create_directory=True, content='all'):
	from resources.lib.indexers import movies, tvshows, episodes

	traktCredentials = trakt.getTraktCredentialsInfo()
	epRegex = '(.+?)[._\s-]?(?:s|season)?(\d{1,2})(?:e|x|-|episode)(\d{1,2})[._\s\(\[-]'
	movieRegex = '(.+?)(\d{4})[._ -\)\[]'

	cached_time, cached_results = cloudCache(mode='get')

	if cached_time != '0' and cached_time != None:
		if control.setting('first.start') == 'true':
			control.setSetting(id='first.start', value='false')
			r = PremiumizeScraper().sources()
			cloudCache(mode='write', data=r)
		else:
			r = cached_results
			
	elif cached_time == '0' or cached_time == None or cached_results == '0' or cached_results == None:
		control.setSetting(id='first.start', value='false')
		r = PremiumizeScraper().sources()
		cloudCache(mode='write', data=r)
		
	r = [i for i in r if i['type'] == 'file']
	r = [i for i in r if i['name'].split('.')[-1] in VALID_EXT]
	r =  sorted(r, key=lambda k: int(k['created_at']), reverse=True)
	if control.setting('metacloud.dialog') == 'true':
		progressDialog = control.progressDialog
		progressDialog.create('Creating Meta DB', '')
		progressDialog.update(0,'Checking your Cloud...')
	total = len(r)
	count = 0
	
	metaItems = []
	metaEpisodes = []
	for result in r:
		count += 1
		isMovie = False
		isTv    = False
		name = result['name']
		prog = (count * 100) / int(total)
		if control.setting('metacloud.dialog') == 'true': progressDialog.update(prog,'This process will run just for items in your cloud not already in the database...', name)	
		season = None
		episode = None
		imdb = None
		tvdb = None
		tmdb = None
		tvshowtitle = None		
		match = re.search(epRegex, name.lower(), re.I)
		if match: 
			isTv = True
			match = match.groups()
			tvTitle    = match[0]
			season     = match[1]	
			episode    = match[2]				
		if isTv == False:
			match2 = re.search(movieRegex, name.lower(), re.I)
			if match2: 
				match2 = match2.groups()

				isMovie = True
				movieTitle = match2[0]
				movieYear  = match2[1]
				
		cm = []	

		id = result['id']
		cacheID = "premiumize-%s" % (id)
		name = result['name'].encode('utf-8')
		name = normalize(name)
		superInfo = {'title': name, 'year':'0', 'imdb':'0'}
		try:
			if progressDialog.iscanceled(): break
		except:
			pass
		try:
			meta = []
			metaData = []
			
			if isMovie == True:

				if content != 'movie' and content != 'all': raise Exception()
				cacheID = cacheID + "-movie"
				getCache  = cache.get_from_string(cacheID, 2000, None)
				if getCache == None: 
					getSearch =	movies.movies().searchTMDB(title=movieTitle, year=movieYear)
					getSearch = getSearch[0]
					if len(getSearch) > 0: cache.get_from_string(cacheID, 2000, getSearch)
				else: getSearch = getCache
				meta = getSearch
				
			elif isTv == True: 

				if content != 'tv' and content != 'all': raise Exception()
	
				getCache  = cache.get_from_string(cacheID, 2000, None)
				if getCache == None: 
					getSearch = tvshows.tvshows().getSearch(title=tvTitle)
					getSearch = getSearch[0]

					if len(getSearch) > 0: cache.get_from_string(cacheID, 2000, getSearch)
				else: getSearch = getCache
				
				tvdb = getSearch['tvdb']
				imdb = getSearch['imdb']
				tvplot = getSearch['plot']
				fanart = getSearch['fanart']
				clearlogo = getSearch['clearlogo'] if 'clearlogo' in getSearch else '0'
				banner = getSearch['banner'] if 'banner' in getSearch else '0'

				year = getSearch['year']
				tvshowtitle = getSearch['title']
				episode = "%02d" % int(episode)
				ss      = "%02d" % int(season)
				
				cacheIDEpisode = cacheID + '-episode-tvdb-%s-season-%s-episode-%s' % (tvdb, ss, episode)
				getCacheEp  = cache.get_from_string(cacheIDEpisode, 720, None)
				if getCacheEp == None: 
					episodeMeta = episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season = season, create_directory = False)
					episodeMeta = [i for i in episodeMeta if "%02d" % int(i['episode']) == episode]
					episodeMeta = episodeMeta[0]
					if len(episodeMeta) > 0: cache.get_from_string(cacheIDEpisode, 720, episodeMeta)
				else: episodeMeta = getCacheEp
				meta = episodeMeta
				meta.update({'premiumizeid': id, 'tvshowimdb': imdb, 'tvshowtvdb': tvdb, 'clearlogo': clearlogo, 'banner': banner})
				metaEpisodes.append(meta)
				
			if create_directory != True: raise Exception()			
			metaData = meta
			metatitle = metaData['title'] if 'title' in metaData else name
			metaposter = metaData['poster'] if 'poster' in metaData else '0'
			metafanart = metaData['fanart'] if 'fanart' in metaData else '0'
			if metaposter == '0' or metaposter == None: metaposter = control.icon
			if metafanart == '0' or metafanart == None: metafanart = control.fanart
			imdb = metaData['imdb'] if 'imdb' in metaData else None
			tvdb = metaData['tvdb'] if 'tvdb' in metaData else None			
			tmdb      = metaData['tmdb'] if 'tmdb' in metaData else None	
			tvshowtitle = metaData['tvshowtitle'] if 'tvshowtitle' in metaData else None
			if isTv == True: metaData.update({'season.poster': metaposter, 'tvshow.poster': metaposter})
			superInfo = metaData

			systitle = urllib.quote_plus(metatitle)			
			if imdb!= None and imdb != '': metaItems.append(imdb)
			if tvdb!= None and tvdb != '': metaItems.append(tvdb)		
			
			if isTv == True:
				
				if tvshowtitle in metaItems: raise Exception()
				metatitle = tvshowtitle
				metaItems.append(tvshowtitle)
				label = "%s" % (tvshowtitle)
				systitle = urllib.quote_plus(superInfo['title'])	
			else: 
				if metatitle in metaItems: raise Exception()
				metaItems.append(metatitle)
				label = metatitle
			playLink = '0'
			sysmeta = urllib.quote_plus(json.dumps(superInfo))				
			year = superInfo['year']

			
			cm = []
			if isTv == True: url = '%s?action=meta_episodes&imdb=%s&tmdb=%s&tvdb=%s' % (sysaddon, imdb, tmdb, tvdb)
			else: url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&meta=%s&id=%s' % (sysaddon, 'resolve', systitle , year, imdb, sysmeta, id)
	
			item = control.item(label=label)	
			art = {}
			art.update({'icon': metaposter, 'thumb': metaposter, 'poster': metaposter})
			# if 'thumb' in metaData and not metaData['thumb'] == '0': art.update({'icon': metaData['thumb'], 'thumb': metaData['thumb']})
			if 'banner' in metaData and not metaData['banner'] == '0': art.update({'banner': metaData['banner']})
			if 'clearlogo' in metaData and not metaData['clearlogo'] == '0': art.update({'clearlogo': metaData['clearlogo']})
			if 'clearart' in metaData and not metaData['clearart'] == '0': art.update({'clearart': metaData['clearart']})
			if 'season.poster' in metaData and not metaData['season.poster'] == '0': art.update({'season.poster': metaposter})

			if traktCredentials == True:
				try:
					if isTv == True: raise Exception()
					indicators = playcount.getMovieIndicators(refresh=True)
					overlay = int(playcount.getMovieOverlay(indicators, imdb))
					if overlay == 7:
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
						meta.update({'playcount': 1, 'overlay': 7})
					else:
						cm.append((watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
						meta.update({'playcount': 0, 'overlay': 6})
				except:
					pass	

				# try:
					# if isTv != True: raise Exception()
					# indicators = playcount.getTVShowIndicators(refresh=True)
					# overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tvdb, season, episode))
					# if overlay == 7:
						# cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode)))
						# meta.update({'playcount': 1, 'overlay': 7})
					# else:
						# cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode)))
						# meta.update({'playcount': 0, 'overlay': 6})
				# except:
					# pass					
			superInfo.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
			superInfo.update({'tmdb_id': tmdb})
			superInfo.update({'mediatype': 'movie'})
			if isTv == True: superInfo.update({'mediatype': 'tvshow'})
			if "cast" in superInfo: del superInfo['cast']
			superInfo.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(metatitle))})
			try:
				superInfo.update({'duration': str(int(superInfo['duration']) * 60)})
			except:
				pass		
			superInfo = dict((k, v) for k, v in superInfo.iteritems() if not v == '0')				
			item.setProperty('Fanart_Image', metafanart)
			infolabels = {}
			infolabels.update(superInfo)

			item.setArt(art)
			item.addContextMenuItems(cm)
			if isTv != True: item.setProperty('IsPlayable', 'true')
			
			if isTv == True: 
				del superInfo['plot']
				infolabels = {'plot': tvplot}
				infolabels.update(superInfo)			
				isFolder = True
				
			else: isFolder = False
			item.setInfo(type='Video', infoLabels = infolabels)
			control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)				
		except: pass
		
	try: progressDialog.close()
	except:	pass
	
	if len(metaEpisodes) > 0:
		premiumizeCacheID = 'premiumize-tvshows-meta-scrape'
		cache.get_from_string(premiumizeCacheID, 720, metaEpisodes)
	
	if create_directory == True: 
		contentDir = 'movies'
		if content == 'tv': contentDir = 'tvshows'
		control.content(syshandle, contentDir)	
		control.directory(syshandle, cacheToDisc=True)		

def meta_episodes(imdb=None, tvdb=None, tmdb = None, create_directory=True):
	traktCredentials = trakt.getTraktCredentialsInfo()
	epRegex = '(.+?)[._\s-]?(?:s|season)?(\d{1,2})(?:e|x|-|episode)(\d{1,2})[._\s\(\[-]'
	movieRegex = '(.+?)(\d{4})[._ -\)\[]'
 
	premiumizeCacheID = 'premiumize-tvshows-meta-scrape'
	episodes = cache.get_from_string(premiumizeCacheID, 720, None)

	if imdb != None: r = [i for i in episodes if i['tvshowimdb'] == imdb]
	elif tvdb != None: r = [i for i in episodes if i['tvshowtvdb'] == tvdb]
	try: r = sorted(r, key=lambda x: (int(x['season']), int(x['episode'])))
	except: pass
		
	for result in r:
			id = result['premiumizeid']
			meta = result
			metaData = meta
			metatitle = metaData['title'] if 'title' in metaData else name
			metaposter = metaData['poster'] if 'poster' in metaData else '0'
			metafanart = metaData['fanart'] if 'fanart' in metaData else '0'
			if metaposter == '0' or metaposter == None: metaposter = control.icon
			if metafanart == '0' or metafanart == None: metafanart = control.fanart
			year	= meta['year']
			season = meta['season']
			episode = meta['episode']
			imdb = metaData['imdb'] if 'imdb' in metaData else None
			tvdb = metaData['tvdb'] if 'tvdb' in metaData else None			
			tmdb      = metaData['tmdb'] if 'tmdb' in metaData else None	
			tvshowtitle = metaData['tvshowtitle'] if 'tvshowtitle' in metaData else None
			metaData.update({'season.poster': metaposter, 'tvshow.poster': metaposter})
			superInfo = metaData
			systitle = urllib.quote_plus(metatitle)			

			label = "S%s:E%s - %s" % (season, episode, metatitle)
			systitle = urllib.quote_plus(superInfo['title'])	

			playLink = '0'
			sysmeta = urllib.quote_plus(json.dumps(superInfo))				
			year = superInfo['year']

			cm = []
			url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&meta=%s&id=%s' % (sysaddon, 'resolve', systitle, year, imdb, tmdb, tvdb, season, episode, tvshowtitle, sysmeta, id)

			item = control.item(label=label)	
			art = {}
			art.update({'icon': metaposter, 'thumb': metaposter, 'poster': metaposter})
			if 'thumb' in metaData and not metaData['thumb'] == '0': art.update({'icon': metaData['thumb'], 'thumb': metaData['thumb']})
			if 'banner' in metaData and not metaData['banner'] == '0': art.update({'banner': metaData['banner']})
			if 'clearlogo' in metaData and not metaData['clearlogo'] == '0': art.update({'clearlogo': metaData['clearlogo']})
			if 'clearart' in metaData and not metaData['clearart'] == '0': art.update({'clearart': metaData['clearart']})
			if 'season.poster' in metaData and not metaData['season.poster'] == '0': art.update({'season.poster': metaposter})

			if traktCredentials == True:
				try:
					indicators = playcount.getTVShowIndicators(refresh=True)
					overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tvdb, season, episode))
					if overlay == 7:
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode)))
						meta.update({'playcount': 1, 'overlay': 7})
					else:
						cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode)))
						meta.update({'playcount': 0, 'overlay': 6})
				except:
					pass					
			superInfo.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
			superInfo.update({'tmdb_id': tmdb})

			superInfo.update({'mediatype': 'episode'})
			if "cast" in superInfo: del superInfo['cast']

			try:
				superInfo.update({'duration': str(int(superInfo['duration']) * 60)})
			except:
				pass		
			superInfo = dict((k, v) for k, v in superInfo.iteritems() if not v == '0')				
			item.setProperty('Fanart_Image', metafanart)
			item.setInfo(type='Video', infoLabels = superInfo)
			item.setArt(art)
			item.addContextMenuItems(cm)
			item.setProperty('IsPlayable', 'true')
			control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)				

	if create_directory == True: 
		contentDir = 'episodes'
		control.content(syshandle, contentDir)	
	
		control.directory(syshandle, cacheToDisc=True)		

def meta_library():
	from resources.lib.indexers import movies, tvshows, episodes

	epRegex = '(.+?)[._\s-]?(?:s|season)?(\d{1,2})(?:e|x|-|episode)(\d{1,2})[._\s\(\[-]'
	movieRegex = '(.+?)(\d{4})[._ -\)\[]'

	cached_time, cached_results = cloudCache(mode='get')

	if cached_time != '0' and cached_time != None:
		if control.setting('first.start') == 'true':
			control.setSetting(id='first.start', value='false')
			r = PremiumizeScraper().sources()
			cloudCache(mode='write', data=r)
		else:
			r = cached_results
			
	elif cached_time == '0' or cached_time == None or cached_results == '0' or cached_results == None:
		control.setSetting(id='first.start', value='false')
		r = PremiumizeScraper().sources()
		cloudCache(mode='write', data=r)
		
	r = [i for i in r if i['type'] == 'file']
	r = [i for i in r if i['name'].split('.')[-1] in VALID_EXT]
	r =  sorted(r, key=lambda k: int(k['created_at']), reverse=True)

	progressDialog = control.progressDialogBG
	progressDialog.create('Updating Premiumize Library', '')
	progressDialog.update(0,'Updating Premiumize Library...', 'Please Wait')
	
	total = len(r)
	count = 0
	
	metaItems = []
	metaEpisodes = []
	for result in r:
		count += 1
		isMovie = False
		isTv    = False
		name = result['name']
		prog = (count * 100) / int(total)
		progressDialog.update(prog, 'Updating Premiumize Library', name)	
		season = None
		episode = None
		imdb = None
		tvdb = None
		tmdb = None
		tvshowtitle = None		
		match = re.search(epRegex, name.lower(), re.I)
		if match: 
			isTv = True
			match = match.groups()
			tvTitle    = match[0]
			season     = match[1]	
			episode    = match[2]				
		if isTv == False:
			match2 = re.search(movieRegex, name.lower(), re.I)
			if match2: 
				match2 = match2.groups()

				isMovie = True
				movieTitle = match2[0]
				movieYear  = match2[1]
				
		cm = []	

		id = result['id']
		cacheID = "premiumize-%s" % (id)
		name = result['name'].encode('utf-8')
		name = normalize(name)
		superInfo = {'title': name, 'year':'0', 'imdb':'0'}
		print superInfo
		try:
			if progressDialog.iscanceled(): break
		except:
			pass
		try:
			meta = []
			metaData = []
			
			if isMovie == True:
				cacheID = cacheID + "-movie"
				getCache  = cache.get_from_string(cacheID, 2000, None)
				if getCache == None: 
					getSearch =	movies.movies().searchTMDB(title=movieTitle, year=movieYear)
					getSearch = getSearch[0]
					if len(getSearch) > 0: cache.get_from_string(cacheID, 2000, getSearch)
				else: getSearch = getCache
				meta = getSearch
				
				
				
			elif isTv == True: 
				getCache  = cache.get_from_string(cacheID, 2000, None)
				if getCache == None: 
					getSearch = tvshows.tvshows().getSearch(title=tvTitle)
					getSearch = getSearch[0]

					if len(getSearch) > 0: cache.get_from_string(cacheID, 2000, getSearch)
				else: getSearch = getCache
				
				tvdb = getSearch['tvdb']
				imdb = getSearch['imdb']
				tvplot = getSearch['plot']
				fanart = getSearch['fanart']
				clearlogo = getSearch['clearlogo'] if 'clearlogo' in getSearch else '0'
				banner = getSearch['banner'] if 'banner' in getSearch else '0'

				year = getSearch['year']
				tvshowtitle = getSearch['title']
				episode = "%02d" % int(episode)
				ss      = "%02d" % int(season)
				
				cacheIDEpisode = cacheID + '-episode-tvdb-%s-season-%s-episode-%s' % (tvdb, ss, episode)
				getCacheEp  = cache.get_from_string(cacheIDEpisode, 720, None)
				if getCacheEp == None: 
					episodeMeta = episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season = season, create_directory = False)
					episodeMeta = [i for i in episodeMeta if "%02d" % int(i['episode']) == episode]
					episodeMeta = episodeMeta[0]
					if len(episodeMeta) > 0: cache.get_from_string(cacheIDEpisode, 720, episodeMeta)
				else: episodeMeta = getCacheEp
				meta = episodeMeta
				meta.update({'premiumizeid': id, 'tvshowimdb': imdb, 'tvshowtvdb': tvdb, 'clearlogo': clearlogo, 'banner': banner})
				metaEpisodes.append(meta)
				
			metaData = meta
			metatitle = metaData['title'] if 'title' in metaData else name
			metaposter = metaData['poster'] if 'poster' in metaData else '0'
			metafanart = metaData['fanart'] if 'fanart' in metaData else '0'
			if metaposter == '0' or metaposter == None: metaposter = control.icon
			if metafanart == '0' or metafanart == None: metafanart = control.fanart
			imdb = metaData['imdb'] if 'imdb' in metaData else None
			tvdb = metaData['tvdb'] if 'tvdb' in metaData else None			
			tmdb      = metaData['tmdb'] if 'tmdb' in metaData else None	
			tvshowtitle = metaData['tvshowtitle'] if 'tvshowtitle' in metaData else None
			if isTv == True: metaData.update({'season.poster': metaposter, 'tvshow.poster': metaposter})
			superInfo = metaData
			if isMovie == True: type = 'Movie'
			elif isTv  == True: type = 'Tv'
			else: type = None
			if type != None: library_setup(id, type, superInfo)
		except: pass

	try: progressDialog.close()
	except:	pass
		
	if len(metaEpisodes) > 0:
		premiumizeCacheID = 'premiumize-tvshows-meta-scrape'
		cache.get_from_string(premiumizeCacheID, 720, metaEpisodes)

	control.execute('XBMC.UpdateLibrary(video)')
		
def createLibFolder(path):
    os.makedirs(path)
	
def createStrm(name, id, path):
	systitle = urllib.quote_plus(name)
	content = '%s?action=play_library&name=%s&id=%s' % (sys.argv[0], systitle, str(id))
	file = open(path, 'w')
	file.write(content)
	file.close() 
	
def createNfo(content, type, path):
	if type == 'movie': type = 'movie.nfo'
	else: type = 'tvshow.nfo'
	nfo_path = os.path.join(path, type)
	file = open(nfo_path, 'w')
	file.write(content)
	file.close() 

def nfo_url(type, id):
    tvdb_url = 'http://thetvdb.com/?tab=series&id=%s'
    tmdb_url = 'https://www.themoviedb.org/%s/%s'
    imdb_url = 'http://www.imdb.com/title/%s/'

    if type == 'tvdb':
            return tvdb_url % (str(id))
    elif type == 'tmdb':
            return tmdb_url % (str(id))
    elif type == 'imdb':
            return imdb_url % (str(id))
    else:
            return ''
			
def updateMetaLibrary(force=False):
	timeNow =  str(datetime.datetime.now().strftime('%Y%m%d'))
	lastUpdate = str(control.setting('meta.library.refresh'))
	if int(timeNow) != int(lastUpdate): 
		meta_library()
		control.setSetting(id='meta.library.refresh', value=timeNow)
		
def lib_delete_folder(path):
	import shutil
	try: shutil.rmtree(path)
	except:pass
	for root, dirs, files in os.walk(path , topdown=True):
		dirs[:] = [d for d in dirs]
		for name in files:
			try:
				os.remove(os.path.join(root,name))
				os.rmdir(os.path.join(root,name))
			except: pass
							
		for name in dirs:
			try: os.rmdir(os.path.join(root,name)); os.rmdir(root)
			except: pass
	
def library_setup(id=None, type=None, meta=None):
    movielibraryPath   = xbmc.translatePath(control.setting('meta.library.movies'))
    tvlibraryPath		= xbmc.translatePath(control.setting('meta.library.tv'))
	
    print movielibraryPath
    print tvlibraryPath
	
    if not os.path.exists(movielibraryPath): os.mkdir(movielibraryPath)	
    if not os.path.exists(tvlibraryPath): os.mkdir(tvlibraryPath)	

    imdb = meta['imdb'] if 'imdb' in meta else None
    tvdb = meta['tvdb'] if 'tvdb' in meta else None			
    tmdb = meta['tmdb'] if 'tmdb' in meta else None		
    #if metaPath == None: metaPath = libPathMeta
    if type == 'Movie': 
		title = meta['title']
		year = meta['year']
		if year == '0': year = ''
		transtitle = normalize(title)
		transtitle = re.sub('[\?\!]', '', transtitle)
		print title, transtitle, legal_filename(transtitle)
		folder = make_path(movielibraryPath, transtitle, year)
		create_folder(folder)
		filePath = os.path.join(folder, legal_filename(transtitle) + '.strm')
		print filePath
		if imdb   != '0' and imdb != None: nfo_url_content = nfo_url('imdb', imdb)
		elif tmdb != '0' and tmdb != None: nfo_url_content = nfo_url('tmdb', tmdb)
		else: nfo_url_content = ''
		createStrm(transtitle, id, filePath)
		if nfo_url_content != '': createNfo(nfo_url_content, 'movie', folder)
		
    elif type == 'Tv': 
		title = meta['title']
		tvshowtitle = meta['tvshowtitle']
		year = meta['year']
		if year == '0': year = ''
		season = meta['season']
		episode = meta['episode']
		season = "%02d" % int(season)
		episode = "%02d" % int(episode)
		
		transtitle = normalize(tvshowtitle)
		transtitle = re.sub('[\?\!]', '', transtitle)
		# print title, transtitle, legal_filename(transtitle)
		folder = make_path(tvlibraryPath, transtitle, year)
		create_folder(folder)
		epTitle = "%s S%sE%s" % (transtitle, season, episode)
		filePath = os.path.join(folder, legal_filename(epTitle) + '.strm')

		if tvdb   != '0' and tvdb != None: nfo_url_content = nfo_url('tvdb', tvdb)
		elif imdb != '0' and imdb != None: nfo_url_content = nfo_url('imdb', imdb)
		elif tmdb != '0' and tmdb != None: nfo_url_content = nfo_url('tmdb', tmdb)
		else: nfo_url_content = ''
		createStrm(epTitle, id, filePath)
		if nfo_url_content != '': createNfo(nfo_url_content, 'tv', folder)
		

    # except Exception as e:

		# print ("PREMIUMIZE ERROR:", str(e))		

def new_cloud_cache():
	control.infoDialog('Scraping your Cloud...')	
	r = PremiumizeScraper().sources()
	cloudCache(mode='write', data=r)
	control.infoDialog('New Cache Created...')	
		
def getSearch_movie(movieTitle, movieYear):
	from resources.lib.indexers import movies
	movie = movies.movies().searchTMDB(title=movieTitle, year=movieYear)	
	return movie
	
def getSearch_tv(tvTitle):
	from resources.lib.indexers import tvshows
	tv = tvshows.tvshows().getSearch(title=tvTitle)	
	return tv	
	
def getSearch_episode(tvshowtitle, year, imdb, tvdb, season):
	from resources.lib.indexers import episodes
	episode = episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season = season, create_directory = False)
	return episode

	
def direct_downlaod(id):
	return

def check_cloud(title): 
	inCloud = False
	r = PremiumizeScraper().sources()
	for result in r:
		name = result['name'].encode('utf-8')
		if not cleantitle.get(title) in cleantitle.get(name): continue
		ratio = matchRatio(cleantitle.get(title), cleantitle.get(name))
		return ratio
	
def scrapecloud(title, match, year=None, season=None, episode=None):
	progress = control.progressDialogBG
	filesOnly = control.setting('scraper.filesonly')
	cachedSession = control.setting('cachecloud.remember')
	try:
		cached_time, cached_results = cloudCache(mode='get')
		progress.create('Scraping Your Cloud','Please Wait...')
		
		if cached_time != '0' and cached_time != None:
			if cachedSession == 'true': 
				if control.setting('first.start') == 'true':
					control.setSetting(id='first.start', value='false')
					progress.update(100,'Scraping Your Cloud','Please Wait...')
					r = PremiumizeScraper().sources()
					cloudCache(mode='write', data=r)
				else:
					r = cached_results
					
				try: progress.close()
				except:pass
				try: progress.close()
				except:pass
				
			else:
				cachedLabel = "Cached Cloud: %s" % cached_time
				results = [cachedLabel, 'New Cloud Scrape', '[AUTO] Cached Cloud']
				select = control.selectDialog(results)
				if select == 0: r = cached_results
				elif select == 1: 
					progress.update(100,'Scraping Your Cloud','Please Wait...')
					r = PremiumizeScraper().sources()
					cloudCache(mode='write', data=r)
				elif select == 2: # FORCE NEW CACHE AND AUTO CACHE MODE
					control.setSetting(id='cachecloud.remember', value='true')
					control.setSetting(id='first.start', value='false')
					progress.update(100,'Scraping Your Cloud','Please Wait...')
					r = PremiumizeScraper().sources()
					cloudCache(mode='write', data=r)
				try: progress.close()
				except:pass
				try: progress.close()
				except:pass
		
		else:
			if cachedSession == 'true': 
				control.setSetting(id='first.start', value='false')
				progress.update(100,'Scraping Your Cloud','Please Wait...')
				r = PremiumizeScraper().sources()
				cloudCache(mode='write', data=r)
				try: progress.close()
				except:pass
				try: progress.close()
				except:pass
				
			else:
				progress.update(100,'Scraping Your Cloud','Please Wait...')
				r = PremiumizeScraper().sources()
				cloudCache(mode='write', data=r)
				try: progress.close()
				except:pass
				try: progress.close()
				except:pass				
			
		labels = []
		sources = []
		types = []
		IDs = []
		
		normalSources = []
		exactSources  = []
		
		titleCheck = cleantitle.get(title)
		exactPlay = False
		if season != None:
			epcheck    = "s%02de%02d" % (int(season), int(episode))
			epcheck_2  = "%02dx%02d"  % (int(season), int(episode))
			
			dd_season  = "%02d" % int(season)
			dd_episode = "%02d" % int(episode)
			
			exactCheck_1 = titleCheck + epcheck
			exactCheck_2 = titleCheck + epcheck_2

		else:
			if year == '' or year == None or year == '0': year = ''
			exactCheck_1 = titleCheck + year
			exactCheck_2 = titleCheck + year
		

		for x in r:
			try:
				cm = []
				type = x['type']
				if filesOnly == 'true':
					if type.lower() != 'file': raise Exception()
				fileLabel = type
				id = x['id']
				name = x['name'].encode('utf-8')
				name = normalize(name)

				
				if not titleCheck in cleantitle.get(name): raise Exception()

				normalSources.append(x)
				
				if exactCheck_1 in cleantitle.get(name) or exactCheck_2 in cleantitle.get(name):
					exactSources.append(x)
				else:
					epmixed = re.findall('[._ -]s?(\d+)[e|x](\d+)[._ -]', name.lower())[0]
					s = epmixed[0]
					e = epmixed[1]
					if s == dd_season or s == season:
						if e == dd_episode or e == episode: exactSources.append(x)
			except:pass
			
				
		if len(exactSources) > 0: 
			content = exactSources
			exactPlay = True
				
		else: content = normalSources
		
		for result in content:
			cm = []
			type = result['type']
			fileLabel = type
			id = result['id']
			name = result['name'].encode('utf-8')
			name = normalize(name)
			
			playLink = '0'
			isFolder = True
			isPlayable = 'false'
			url = '0'
			if type == 'file':
				if control.setting('transcoded.play') == 'true':
					try:
						playLink = result['stream_link']
						if not "http" in playLink: playLink = result['link']
						type = 'TRANSCODED'
					except: playLink = result['link']
				else:
					playLink = result['link']
				ext = playLink.split('.')[-1]
				if not ext.lower() in VALID_EXT: continue
				fileLabel = type + " " + str(ext)
				try: 
					size = result['size']
					size = getSize(size)
				except: size = ''
				if size != '': fileLabel = fileLabel + " | " + str(size)
				isFolder = False
				isPlayable = 'true'
				url = playLink
				#AUTOPLAY
				if exactPlay == True and control.setting('scraper.autoplay') == 'true': return url, id
				
			label = "[B]" + fileLabel.upper() + " |[/B] " + str(name) 
			labels.append(label)
			sources.append(url)
			types.append(type)
			IDs.append(id)
		
		try: progress.close()
		except:pass
		try: progress.close()
		except:pass
		
		if len(sources) < 1: return '0'
		select = control.selectDialog(labels)
		if select == -1: return '0'
		
		selected_type = types[select]
		
		selected_url = sources[select]

		selected_id = IDs[select]
		
		if selected_type != 'file': 
			selected_url = dialogselect_folder(selected_id)
		return selected_url	, selected_id
	except:
		try: progress.close()
		except:pass
		try: progress.close()
		except:pass		

def dialogselect_folder(id):
	folder = premiumizeFolder + id
	url = urlparse.urljoin(premiumize_Api, folder) 
	r = reqJson(url)
	r = r['content']
	labels = []
	sources = []
	types = []
	IDs = []
	for result in r:
		type = result['type']
		fileLabel = type
		id = result['id']
		name = result['name'].encode('utf-8')
		name = normalize(name)
		playLink = '0'
		isFolder = True
		isPlayable = 'false'
		url = '0' 
		if type == 'file':
			playLink = result['link']
			ext = playLink.split('.')
			fileLabel = type + " " + str(ext[-1])
			try: 
				size = result['size']
				size = getSize(size)
			except: size = ''
			if size != '': fileLabel = fileLabel + " | " + str(size)			
			isFolder = False
			isPlayable = 'true'
			url = playLink
		label = "[B]" + fileLabel.upper() + " |[/B] " + str(name) 
		IDs.append(id)
		labels.append(label)
		sources.append(url)
		types.append(type)
		IDs.append(id)
	select = control.selectDialog(labels)
	if select == -1: return '0'
	selected_type = types[select]
	selected_url = sources[select]
	selected_id = IDs[select]
	if selected_type != 'file': 
		selected_url = dialogselect_folder(selected_id)
	return selected_url
	
		
def transferList():
	clearfinished = '%s?action=%s' % (sysaddon, 'premiumizeClearFinished')
	item = control.item(label='Clear Finished Transfers')
	control.addItem(handle=syshandle, url=clearfinished, listitem=item, isFolder=False)
	url = urlparse.urljoin(premiumize_Api, premiumizeTransfer) 
	r = reqJson(url)
	r = r['transfers']
	
	for result in r:
		cm = []
		status = result['status']
		progress = result.get('progress')
		file_id = result['file_id']
		if file_id != '' and file_id != None: isFolder = False
		else: isFolder = True

		id = result['id']
		folder_id = result['folder_id']
		name = result['name'].encode('utf-8')
		name = normalize(name)
		superInfo = {'title': name, 'year':'0', 'imdb':'0'}
			
		if not status == 'finished': 
			if not progress == '0':
				try:
					progress = re.findall('\.(\d+)', str(progress))[0]
					progress = progress[:2]
				except: progress = ''
				try:
					message = result['message']
					
				except: message = ''								
			label = "[B]" + status.upper() + "[/B] [" + str(progress) + " %] " + message  + " | " + name
		else: label = "[B]" + status.upper() + "[/B] | " + name

		
		url = '%s?action=%s&id=%s' % (sysaddon, 'premiumizeOpenFolder', folder_id)
		
		sysmeta = urllib.quote_plus(json.dumps(superInfo))	
		systitle = urllib.quote_plus(superInfo['title'])		
		if isFolder == False:
			playLink = getIDLink(file_id)
			isPlayable = 'true'
			try: playLink = urllib.quote_plus(playLink)
			except: pass	
			url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&meta=%s&id=%s' % (sysaddon, playLink, systitle , superInfo['year'], superInfo['imdb'], sysmeta, file_id)		
			if control.setting('downloads') == 'true': cm.append(('Download from Cloud', 'RunPlugin(%s?action=download&name=%s&url=%s&id=%s)' % (sysaddon, name, url, id)))
			cm.append(('Queue Item', 'RunPlugin(%s?action=queueItem)' % sysaddon))				
			

		cm.append(('Delete from Cloud', 'RunPlugin(%s?action=premiumizeDeleteItem&id=%s&type=torrent)' % (sysaddon, id)))
		item.setArt({'icon': control.icon, 'thumb': control.icon})
		item.setProperty('Fanart_Image', control.addonFanart())
		
		item = control.item(label=label)
		item.addContextMenuItems(cm)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
				
	control.directory(syshandle, cacheToDisc=True)

def clearfinished():
    url = urlparse.urljoin(premiumize_Api, premiumizeClearFinished) 
    r = reqJson(url)
    control.refresh()
	
def DeleteAllTypes(id, mode='normal', autodelete='false'):
	try:
		if id == '' or id == '0' or id == None or id == 'false': raise Exception()
		data = {'id': id }
		
		u = urlparse.urljoin(premiumize_Api, premiumizeItemDetails) 
		details = reqJson(u, data=data)
		filename = details['name']	
		folderId = details['folder_id']	
		
		url = urlparse.urljoin(premiumize_Api, premiumizeDeleteItem) 
		r = reqJson(url, data=data)
			#print ("PREMIUMIZE DELETE ITEM", url, r)
		try:
			if mode != 'full': raise Exception()

			ext = filename.split('.')
			ext = '.%s' % ext[-1]
			
			if folderId == '0' or folderId == None or folderId == '': raise Exception()
			x = premiumizeFolder + str(folderId)
			folder = urlparse.urljoin(premiumize_Api, x)
			folder = reqJson(folder)
			folderNameOrig = folder['name']
			if folderNameOrig.lower() == 'root': raise Exception()
			folderName = folderNameOrig + ext
			folderClear = re.sub('\n|([[].+?[]])|([(].+?[)])|\s', '', folderName)
			filenameClean = re.sub('\n|([[].+?[]])|([(].+?[)])|\s', '', filename)
			if autodelete == 'true':
				if folderClear.lower() == filenameClean.lower(): 
					deleteItem(folderId, 'folder')
					raise Exception()			
			else:
				query = control.yesnoDialog('Found Parent Folder: ', folderNameOrig , 'Do you want to delete it?', nolabel='No', yeslabel='Yes')
				if query == 1: deleteItem(folderId, 'folder')
		except:pass
	except:pass

def DeleteDialog(id):
	query = control.yesnoDialog('Premiumize Cloud', 'Do you want to delete the file from your cloud?' ,'', nolabel='No', yeslabel='Yes')
	if query == 1: # YES
		DeleteAllTypes(id, mode='full')
		
def AutoDelete(id):
	DeleteAllTypes(id, mode='full', autodelete='true')
	
def add_file():
    dialog = xbmcgui.Dialog()
    path = dialog.browse(type=1, heading='Select File to Add - Torrent/Magnet', shares='files',useThumbs=False, treatAsFolder=False, enableMultiple=False)
    if path:
        f = xbmcvfs.File(path, 'rb')
        download = f.read()
        f.close()
        if download.endswith('\n'):
            download = download[:-1]
        add_download(download, path)	
			
            
def add_download(download, path):
    if download:
        try:
            file_name = os.path.basename(path)
            download_type = 'nzb' if path.lower().endswith('nzb') else 'torrent'
            CloudDownload(download, download_type)
        except:pass
			
			
def CloudDownload(download, download_type, folder_id=None, file_name=None):
        url = urlparse.urljoin(premiumize_Api, premiumizeAdd) 
        data = {'type': download_type}
        if folder_id is not None:
            data['folder_id'] = folder_id
        
        if download.startswith('http') or download.startswith('magnet'):
            data = {'src': download}
            r = reqJson(url, data=data)
            status = r['status']
            if status == 'error': 
				mess = r['message']
				control.infoDialog(mess, time=5000)
            else: control.infoDialog(status, time=5000)
        else:
            file_name = 'dummy.' + download_type
            mime_type = 'application/x-nzb' if download_type == 'nzb' else 'application/x-bittorrent'
            multipart_data = '--%s\n' % (BOUNDARY)
            multipart_data += 'Content-Disposition: form-data; name="src"; filename="%s"\n' % (file_name)
            multipart_data += 'Content-Type: %s\n\n' % (mime_type)
            multipart_data += download
            multipart_data += '\n--%s--\n' % (BOUNDARY)
			
            data = {'type': 'torrent'}

            uri = '/api/transfer/create?'
            url = premiumize_Api + uri + urllib.urlencode(data) 

            r = reqJson(url, multipart_data=multipart_data)
            status = r['status']
            if status == 'error': 
				mess = r['message']
				control.infoDialog(mess, time=5000)
            else: control.infoDialog(status, time=5000)	
			
			
			
def cloudCache(mode='write', data=None):
	control.makeFile(control.dataPath)
	DBFile = control.cloudFile
				
	if mode == 'write':
		try:
			timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			payload = {'time': timeNow}
			payload['items'] = data
			with open(DBFile, 'w') as file:	json.dump(payload, file, indent=2)
		except:pass
		
	elif mode == 'get':
		try:
			with open(DBFile, 'r') as file:	
				data = json.load(file)
				#print ("PREMIUMIZE CACHE", file)
				items = data['items']
				#print ("PREMIUMIZE CACHE", items)
				time  = data['time']
				return time, items
		except:
			return '0', '0'
	
	elif mode == 'new':
		try:
			data = PremiumizeScraper().sources()

			timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			payload = {'time': timeNow}
			payload['items'] = data
			with open(DBFile, 'w') as file:	json.dump(payload, file, indent=2)
		except:
			pass
		
			
	
	
		
			

def matchRatio(txt, txt2, amount=None):
	try:
		ratio = SequenceMatcher(None, txt, txt2).ratio()
		numb = str(ratio)
		perc = "{:.0%}".format(float(numb))
		return str(perc)
	except: return '0'
	
def normalize(txt):
    txt = re.sub(r'[^\x00-\x7f]',r'', txt)
    return txt
	
def legal_filename(filename):
        try:
            filename = filename.strip()
            filename = re.sub(r'(?!%s)[^\w\-_\.]', '.', filename)
            filename = re.sub('\.+', '.', filename)
            filename = re.sub(re.compile('(CON|PRN|AUX|NUL|COM\d|LPT\d)\.', re.I), '\\1_', filename)
            xbmc.makeLegalFilename(filename)
            return filename
        except:
            return filename
			
def create_folder(folder):
        try:
            folder = xbmc.makeLegalFilename(folder)
            control.makeFile(folder)

            try:
                if not 'ftp://' in folder: raise Exception()
                from ftplib import FTP
                ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(folder)
                ftp = FTP(ftparg[0][2], ftparg[0][0], ftparg[0][1])
                try:
                    ftp.cwd(ftparg[0][4])
                except:
                    ftp.mkd(ftparg[0][4])
                ftp.quit()
            except:
                pass
        except:
            pass

def write_file(path, content):
        try:
            path = xbmc.makeLegalFilename(path)
            if not isinstance(content, basestring):
                content = str(content)

            file = control.openFile(path, 'w')
            file.write(str(content))
            file.close()
        except Exception as e:
            pass

def make_path(base_path, title, year='', season=''):
        title = re.sub('[\:]', '', title)
        show_folder = re.sub(r'[^\w\-_\. ]', '_', title)
        show_folder = '%s (%s)' % (show_folder, year) if year else show_folder
        path = os.path.join(base_path, show_folder)
        if season:
            path = os.path.join(path, 'Season %s' % season)
        return path
			
def getSize(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'B' if 0 == B > 1 else 'B')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)

def cleantitle_get(title):
    if title == None: return
    title = re.sub('&#(\d+);', '', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|([[].+?[]])|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', ' ', title).lower()
    return title		  

def get_platform():
    platforms = {
        'linux1': 'linux',
        'linux2': 'linux',
        'darwin': 'osx',
        'win32': 'win'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]
	

import libThread	

class library_play:
    def __init__(self):
        self.list = []
        self.threads = []

    def play(self, name, id):
		self.url = getIDLink(id)
		self.OriginalTitle = name
		self.ValidMeta = False
		threads = []
		tv_threads = []		
		try:
			rpc = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "id": "1"}
			rpc = json.dumps(rpc)
			result = xbmc.executeJSONRPC(rpc)
			result = json.loads(result)
			result = result['result']['movies']
			for item in result: threads.append(libThread.Thread(self.movies_meta, item))
			[i.start() for i in threads]
			[i.join()  for i in threads]
						

		except: pass
		
		try:
			if self.ValidMeta == True: raise Exception()
			rpc = {"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "id": "1"}
			rpc = json.dumps(rpc)
			result = xbmc.executeJSONRPC(rpc)
			result = json.loads(result)
			result = result['result']['episodes']
			for item in result:	tv_threads.append(libThread.Thread(self.tv_meta, item))
			[i.start() for i in tv_threads]
			[i.join()  for i in tv_threads]			

		except: pass
		if self.ValidMeta == False: libPlayer(self.OriginalTitle, self.url, '', 'none')
		
		
    def tv_meta(self, item):
		try:
			if self.ValidMeta == True: raise Exception()
			xbmc_id = item['episodeid']							# , "fanart", "title", "originaltitle", "season", "episode", "plot", "thumbnail", "title", "art", "file"
			rpc_file = {"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["tvshowid", "title", "originaltitle", "season", "episode", "plot", "thumbnail", "art", "file"], "episodeid": int(xbmc_id)}, "id": "1"}
			rpc_file = json.dumps(rpc_file)
			result_file = xbmc.executeJSONRPC(rpc_file)	
			result_file = json.loads(result_file)	

			result_file = result_file['result']['episodedetails']
			title = result_file['title']
			file  = result_file['file']
			if self.OriginalTitle in file: 
				self.ValidMeta = True
				libPlayer(title, self.url, xbmc_id, 'episode')
		except:pass
		

    def movies_meta(self, item):
		try:
			if self.ValidMeta == True: raise Exception()
			xbmc_id = item['movieid']
			rpc_file = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["imdbnumber", "title", "art", "file"], "movieid": int(xbmc_id)}, "id": "1"}
			rpc_file = json.dumps(rpc_file)
			result_file = xbmc.executeJSONRPC(rpc_file)	
			result_file = json.loads(result_file)		
					
			result_file = result_file['result']['moviedetails']
			title = result_file['title']
			file  = result_file['file']
			if self.OriginalTitle in file: 
				self.ValidMeta = True
				libPlayer(title, self.url, xbmc_id, 'movie')
		except:pass
		
		
	
class PremiumizeScraper:
    def __init__(self):
        self.list = []
        self.threads = []

    def sources(self):
        try:
            threads = []
	
            url = urlparse.urljoin(premiumize_Api, premiumizeRootFolder)
            r = reqJson(url)
            r = r['content']
            for item in r:
                id = str(item['id'])
                self.list.append(item)
                if item['type'] == 'folder': 
					threads.append(libThread.Thread(self.scrapeFolder, id))
            #print ("PREMIUMIZESCRAPER", threads)
            [i.start() for i in threads]
            [i.join() for i in threads]	
            return self.list
        except:
            return

    def scrapeFolder(self, id):
        s_threads = []
        try:
            u = premiumizeFolder + id
            url = urlparse.urljoin(premiumize_Api, u)
            r = reqJson(url)
            r = r['content']
            for item in r:
                self.list.append(item)
                if item['type'] == 'folder': 
					s_threads.append(libThread.Thread(self.scrapeFolder, item['id']))
            [i.start() for i in s_threads]	
            [i.join() for i in s_threads]					
        except:
            return
		
		

