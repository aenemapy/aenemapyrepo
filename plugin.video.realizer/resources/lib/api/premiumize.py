# -*- coding: utf-8 -*-
from resources.lib.modules import control, cleantitle, client
import requests
import os,sys,re,json,urllib,urlparse
import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from difflib import SequenceMatcher
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
premiumizeCustomerID = control.setting('premiumize.customer_id')
premiumizePIN = control.setting('premiumize.pin')

addonInfo     = xbmcaddon.Addon().getAddonInfo
profilePath   = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
libraryPath   = xbmc.translatePath(control.setting('library.path'))
manualLibrary = xbmc.translatePath(control.setting('library.manual'))
libPathMeta   = control.setting('library.path')

if control.setting('premiumize.tls') == 'true': premiumize_Api = 'https://www.premiumize.me'
else: premiumize_Api = 'http://www.premiumize.me'
premiumizeInfo = '/api/account/info'
premiumizeAdd = '/api/transfer/create'
premiumizeTransfer = '/api/transfer/list'
premiumizeClearFinished = '/api/transfer/clearfinished'
realizerootFolder = '/api/folder/list'
premiumizeFolder = '/api/folder/list?id='
premiumizeDeleteItem = '/api/item/delete'
realizerenameItem = '/api/item/rename'
premiumizeItemDetails = '/api/item/details'
USER_AGENT = 'Premiumize Addon for Kodi'
BOUNDARY = 'X-X-X'
data = {}
params = {}

VALID_EXT = ['mkv', 'avi', 'mp4' ,'divx', 'mpeg', 'mov', 'wmv', 'avc', 'mk3d', 'xvid', 'mpg']

def reqJson(url, params=None, data=None, multipart_data=None):
    if data == None: data = {}
    data['customer_id'] = premiumizeCustomerID
    data['pin'] = premiumizePIN
    if multipart_data != None: 
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
		headers['Content-Type'] = 'multipart/form-data; boundary=%s' % (BOUNDARY)
		try: result = requests.post(url, data=multipart_data, headers=headers, timeout=30).json()
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)
    else:
		try: result = requests.post(url, params=params, data=data, timeout=30).json()
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)	
    return result
	
def req(url, params=None, data=None, multipart_data=None):
    if data == None: data = {}
    data['customer_id'] = premiumizeCustomerID
    data['pin'] = premiumizePIN
    if multipart_data != None: 
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
		headers['Content-Type'] = 'multipart/form-data; boundary=%s' % (BOUNDARY)
		try: result = requests.post(url, data=multipart_data, headers=headers, timeout=30).content
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)
    else:
		try: result = requests.post(url, params=params, data=data, timeout=30).content
		except requests.Timeout as err: control.infoDialog('PREMIUMIZE API is Down...', time=3000)	
    return result
	
def info():
    label = 'CANNOT GET ACCOUNT INFO'
    url = urlparse.urljoin(premiumize_Api, premiumizeInfo)
    r = reqJson(url)
    status = r['status']
    if status == 'success':
		expire = r['premium_until']
		limits = r['limit_used']
		numb = str(limits)
		perc = "{:.0%}".format(float(numb))
		label = 'ACCOUNT: PREMIUM - LIMITS USED:  ' + str(perc)
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
	else: renameUrl = realizerenameItem
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
	req = urlparse.urljoin(premiumize_Api, premiumizeItemDetails)
	data = {'id': id}
	r = reqJson(req, data=data)
	file = r['link']
	return file

def downloadFolder(name, id):
	data = {'folders[]': id}
	req = urlparse.urljoin(premiumize_Api, '/api/zip/generate')
	u = reqJson(req, data=data)
	zipLink = u['location']
	name = name.replace(' ','_') + ".zip"
	from resources.lib.modules import downloader
	loc = control.setting('download.path')
	dest = os.path.join(loc, name)
	downloader.downloadZip(zipLink, dest, name)
	
def createLibFolder(path):
    os.makedirs(path)
	
def createStrm(name, id, path):
	content = '%s?action=play_library&name=%s&id=%s' % (sys.argv[0], name, str(id))
	file = open(path, 'w')
	file.write(content)
	file.close() 

def addtolibrary_service(id=None, path=None, selectivePath=None, pDialog=None, type=None, name=None):
	modes = ['Normal Mode', 'Cloud Sync for this Folder']
	if type.lower() != 'folder': 
		type = 'file'
		selectType = 0
	else: selectType = control.selectDialog(modes)
	
	if selectType   == 1: # CLOUD SYNC
		sType = ['Movies', 'Tv Shows', 'Mixed', 'None']
		select = control.selectDialog(sType, heading='Put Item in SubFolder')
		if select   == 0: selectivePath = 'Movies'
		elif select == 1: selectivePath = 'Tvshows'
		elif select == 2: selectivePath = 'Mixed'
		elif select == 3: selectivePath = ''
		if selectivePath == None: selectivePath = ''		
		selective_update(id=id, name=name, selectivePath=selectivePath, mode='new')
		control.infoDialog('Library Service Started... Please Wait')
		r = library_setup(id=id, path=path, selectivePath=selectivePath, pDialog=pDialog, type=type, name=name)
		control.infoDialog('Library Process Complete')
		control.execute('UpdateLibrary(video)')
		
	elif selectType == 0: # NORMAL MODE
		sType = ['Movies', 'Tv Shows', 'Mixed', 'None']
		select = control.selectDialog(sType, heading='Put Item in SubFolder')
		if select   == 0: selectivePath = 'Movies'
		elif select == 1: selectivePath = 'Tvshows'
		elif select == 2: selectivePath = 'Mixed'
		elif select == 3: selectivePath = ''
		if selectivePath == None: selectivePath = ''
		control.infoDialog('Library Service Started... Please Wait')
		r = library_setup(id=id, path=path, selectivePath=selectivePath, pDialog=pDialog, type=type, name=name)
		control.infoDialog('Library Process Complete')
		control.execute('UpdateLibrary(video)')	

def selective_update(id=None, name=None, selectivePath=None, mode='update', deleteold=False):
	control.makeFile(control.dataPath)
	DBFile = control.selectiveLibrary
	newData = []
	dupes   = []
	if mode == 'get':
		try:
			with open(DBFile, 'r') as file:	
				data = json.load(file)
				try: time = data['time']
				except: time = ''
				data = data['items']
				return data, time
		except: return '', ''

	
	if mode == 'delete':
		try:
			with open(DBFile, 'r') as file:	
				data = json.load(file)
				items = data['items']
				
				for y in items:
					if y['type'] == 'library_selective_sync': 
						if not y['id'] == id:
							dupes.append(name)
							newData.append(y)

				import datetime
				timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
				payload = {'time': timeNow}
				payload['items'] = newData
			
				with open(DBFile, 'w') as file:	json.dump(payload, file, indent=2)
				return time, items
		except:pass
		
	elif mode == 'update':
		try:
			with open(DBFile, 'r') as file:	
				data = json.load(file)
				items = data['items']

				for y in items:
					if y['type'] == 'library_selective_sync': 
						if not y['id'] in dupes:
							dupes.append(name)
							newData.append(y)
							
				time  = data['time']
				
				import datetime
				timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
				payload = {'time': timeNow}
				payload['items'] = newData
	
				for x in newData: library_setup(id=x['id'], name=x['name'], selectivePath=x['selectivePath'], type='folder', deleteold=deleteold)
			
			with open(DBFile, 'w') as file:	json.dump(payload, file, indent=2)
									
		except:
			return '0', '0'
	
	elif mode == 'new':
		try:
		
			import datetime
			timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			payload = {'time': timeNow}
			data    = {'id': id, 'name': name , 'selectivePath': selectivePath, 'type': 'library_selective_sync'}
			newData.append(data)
			try: 
				with open(DBFile, 'r') as file:	
					x = json.load(file)
					items = x['items']
					for y in items:
						if y['type'] == 'library_selective_sync': 
							if not y['id'] == id:
								dupes.append(name)
								newData.append(y)
			except:pass
			
			payload['items'] = newData
			
			with open(DBFile, 'w') as file:	json.dump(payload, file, indent=2)
		except:
			pass
	
def selectivelibrary_nav():
	r , lastUpdate = selective_update(mode='get')
	try:
		label = 'Last Sync: ' + str(lastUpdate)
		item = control.item(label=label)

		item.setArt({'icon': control.icon, 'thumb': control.icon})
		item.setProperty('Fanart_Image', control.addonFanart())
		control.addItem(handle=syshandle, url='0', listitem=item, isFolder=False)
	except:pass
	
	for item in r:
		try:
			id = item['id']
			name = item['name']
			label = name
			url = '%s?action=%s&id=%s&name=%s' % (sysaddon, 'selectiveLibraryManager', id, name)
			item = control.item(label=label)

			item.setArt({'icon': control.icon, 'thumb': control.icon})
			item.setProperty('Fanart_Image', control.addonFanart())
			control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
		except:pass
	control.directory(syshandle, cacheToDisc=False)

def selectiveLibraryManager(id, name):
	modes = ['Delete From Auto Sync', 'Force Update']
	select = control.selectDialog(modes)
	if select   == 0: selective_update(id=id, name=name, mode='delete')
	elif select == 1: selective_update(id=id, name=name, mode='update')
	control.refresh()
		
def library_service(id=None, path=None, selectivePath=None, pDialog=None, type=None, name=None):
	control.infoDialog('Library Service Started... Please Wait')
	r = library_setup(id=id, path=path, selectivePath=selectivePath, pDialog=pDialog, type=type, name=name)
	control.infoDialog('Library Process Complete')
	control.execute('UpdateLibrary(video)')	
	
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
	
def library_setup(id=None, path=None, selectivePath=None, pDialog=None, type=None, name=None, originalPath=None, deleteold=False):
    data = None
    CONTENT = []
    #print ("LIBRARY SETUP", type, name)
    if not os.path.exists(libraryPath): os.mkdir(libraryPath)	
	
    #if metaPath == None: metaPath = libPathMeta
    if path == None: libPath = libraryPath
    else: libPath = path
    if selectivePath != None:
		selectivePath = os.path.join(libraryPath, selectivePath)
		libPath = selectivePath
	
    if id == None: url = urlparse.urljoin(premiumize_Api, realizerootFolder)
    else:
		if type == 'file': 	# MANUAL ADD TO LIBRARY FILE
			url = urlparse.urljoin(premiumize_Api, premiumizeItemDetails)
			data = {'id': id}
		else:
			folderId = premiumizeFolder + id
			url = urlparse.urljoin(premiumize_Api, folderId)
			try: 
				if name == None or name == '' or name == '0': raise Exception() 
				if originalPath == 'none': originalPath = os.path.join(libPath, name)
				libPath = os.path.join(libPath, name)
					
				if deleteold == True: lib_delete_folder(libPath)

						
				createLibFolder(libPath)
			except:pass
    
    if originalPath == None: originalPath = libraryPath			
    SUBS_PATH = os.path.join(originalPath, 'SUBS')
    try: createLibFolder(SUBS_PATH)
    except:pass

    r = reqJson(url, data=data)
    # if isinstance(r, list): CONTENT = r['content']
	
    if type == 'file': CONTENT.append(r)
    else: CONTENT = r['content']

    try:
		for item in CONTENT:
			#print ("ADDING ITEM", item)
			try:
				name = item['name'].encode('utf-8')
				
				if item['type'] == 'folder':
					id = item['id']
					try: # WORKAROUND FOR WINDOWS PATHS LONGHER THAN 260
						if int(len(libPath)) < 250: raise Exception()
						platform = get_platform()
						if platform != 'win': raise Exception()
						libPath = '\\\\?\\' + libPath
					except: pass
					library_setup(id=id, path=libPath, name=name, originalPath=originalPath)
					# print path
				else:
					id = item['id']
					link = item['link']
					transname = os.path.splitext(name)[0].encode('utf-8')
					#print ("PREMIUMIZE NAMES", transname)
					ext       = name.split('.')[-1].encode('utf-8')
					#print ("PREMIUMIZE NAMES EXTENSION >>>", ext)
					if ext in VALID_EXT:
						
						filename = transname + '.strm'
						#print ("PREMIUMIZE NAMES 3", filename, link)
						path = os.path.join(libPath, filename)
						path = os.path.normpath(path)
						try:
							if int(len(path)) < 250: raise Exception()
							platform = get_platform()
							if platform != 'win': raise Exception()
							path = '\\\\?\\' + path

						except: pass
					
						#print ("PREMIUMIZE NAMES 4", path)
						try: createStrm(filename, id, path)
						except: pass
						
					elif str(ext).lower() == 'srt': 
						filename = name
						path = os.path.join(SUBS_PATH, filename)
						try: downloadFileToLoc(link, path)
						except: pass
				try: pDialog.close()
				except:pass				
			except:pass


    except Exception as e:

		print ("PREMIUMIZE ERROR:", str(e))
		
def downloadFileToLoc(link, path):
	from resources.lib.modules import downloadzip
	downloadzip.silent_download(link, path)
	

def getFolder(id, meta=None, list=False):
	from resources.lib.indexers import movies, tvshows
	try:
		if id == 'root': url = urlparse.urljoin(premiumize_Api, realizerootFolder) 
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

			try:
				if meta != None and meta != '': raise Exception()
				try:
					if control.setting('tvshows.meta') != 'true': raise Exception()
					sxe_pattern = '(.+?)[._ -]season[._ -]([0-9]+)'
					sxe_pattern2 = '(.*?)[._ -]s(\d{1,2})[._ -ex]'
					sxe_pattern3 = '{._ -\[}TV{._ -\]}(.*?)\((\d{4})\)'
					matchSeason = re.search(sxe_pattern, name.lower())
					matchSeason2 = re.search(sxe_pattern2, name.lower())
					matchShow = re.compile('\[TV\]\s*(.*?)\((\d{4})\)').findall(name)
					if matchShow:
						isFullShow = True
						title = matchShow[0][0]
						year = matchShow[0][1]
						isMovie = False
					elif matchSeason:
						title, season = matchSeason.groups()
						isMovie = False
					elif matchSeason2:
						title, season = matchSeason2.groups()
						isMovie = False

				except: pass
				
				try:
					if control.setting('movies.meta') != 'true': raise Exception()
					if isMovie == True:
						cleanName = cleantitle_get(name)
						patternFull        = '(.*?)[._ -](\d{4})?(?:[._ -]\d+[pP])'
						pattern            = '(.*?)(\d{4}).*'
						match = re.search(patternFull, cleanName, re.I)
						match2 = re.search(pattern, cleanName)
											
						if match:
							isMovie = True
							title, year = match.groups()
						elif match2:
							isMovie = True
							title, year = match2.groups()
				except: pass
				
				title = cleantitle.query(title.encode('utf-8'))
				
				systitle = urllib.quote_plus(title)
				
				if isMovie == True:	
					getSearch =	movies.movies().getSearch(title=systitle)
					metaData = [i for i in getSearch if cleantitle.get(title) == cleantitle.get(i['title']) and i['year'] == year]

				else:
					if isFullShow == True:
						getSearch = tvshows.tvshows().getSearch(title=systitle)
						metaData = [i for i in getSearch if cleantitle.get(title) == cleantitle.get(i['title']) and year == i['year']]
					else:
						getSearch = tvshows.tvshows().getSearch(title=systitle)
						metaData = [i for i in getSearch if cleantitle.get(name).startswith(cleantitle.get(i['title']))]
						
				metaData = metaData[0]
				metarating = metaData['rating'] if 'rating' in metaData else '0'
				metavotes = metaData['votes'] if 'votes' in metaData else '0'	
				metatitle = metaData['title'] if 'title' in metaData else '0'
				metayear = metaData['year'] if 'year' in metaData else '0'
				metaposter = metaData['poster'] if 'poster' in metaData else '0'
				metaplot = metaData['plot'] if 'plot' in metaData else '0'
				metafanart = metaData['fanart'] if 'fanart' in metaData else '0'
				if metaposter == '0' or metaposter == None: metaposter = control.icon
				if metafanart == '0' or metafanart == None: metafanart = control.fanart
				metagenre = metaData['genre'] if 'genre' in metaData else '0'
				metaimdb = metaData['imdb'] if 'imdb' in metaData else '0'
				metatvdb = metaData['tvdb'] if 'tvdb' in metaData else '0'				
				metaduration = metaData['duration'] if 'duration' in metaData else '0'	
				superInfo = {'title': metaData['title'], 'genre': metagenre, 'year': metayear, 'poster': metaposter, 'tvdb': metatvdb, 'imdb': metaimdb, 'fanart': metafanart, 'plot': metaplot, 'rating':metarating, 'duration':metaduration}
				artMeta = True
			
			except: pass
			
			#print ("realizer FOLDER 1", superInfo)			
			playLink = '0'
			isFolder = True
			isPlayable = 'false'
					
			if meta != None and meta != '':
				artMeta = True
				items = json.loads(str(meta))
				superInfo = {'title': items['title'], 'genre': items['genre'], 'year': items['year'], 'poster': items['poster'], 'imdb': items['imdb'], 'fanart': items['fanart'], 'plot':items['plot'], 'rating':items['rating'], 'duration':items['duration']}

			url = '%s?action=%s&id=%s' % (sysaddon, 'premiumizeOpenFolder', id)
			
			sysmeta = urllib.quote_plus(json.dumps(superInfo))				
			year = superInfo['year']
			imdb = superInfo['imdb']
			systitle = urllib.quote_plus(superInfo['title'])
		
			if artMeta == True: 
				if isMovie == False: 
					cm.append(('Browse Cloud Folder', 'Container.Update(%s)' % (url)))
					url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s' % (sysaddon, superInfo['title'], superInfo['year'], superInfo['imdb'], superInfo['tvdb'], season)
								
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
				
				try: playLink = urllib.quote_plus(playLink)
				except: pass					
				
				url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&meta=%s&id=%s' % (sysaddon, playLink, systitle , year, imdb, sysmeta, id)
				cm.append(('Queue Item', 'RunPlugin(%s?action=queueItem)' % sysaddon))					
				if control.setting('downloads') == 'true': cm.append(('Download from Cloud', 'RunPlugin(%s?action=download&name=%s&url=%s&id=%s)' % (sysaddon, name, url, id)))
			else: cm.append(('Download Folder (Zip)', 'RunPlugin(%s?action=downloadZip&name=%s&id=%s)' % (sysaddon, name, id)))
			
			cm.append(('Delete from Cloud', 'RunPlugin(%s?action=premiumizeDeleteItem&id=%s&type=%s)' % (sysaddon, id, type)))
			cm.append(('Rename Item', 'RunPlugin(%s?action=realizerename&id=%s&type=%s&title=%s)' % (sysaddon, id, type, name)))
			
			label = "[B]" + fileLabel.upper() + " |[/B] " + str(name) 
			item = control.item(label=label)
			#item.setProperty('IsPlayable', isPlayable)	
			cm.append(('Add To Library', 'RunPlugin(%s?action=addToLibrary&id=%s&type=%s&name=%s)' % (sysaddon, id, type, name)))
			
			if artMeta == True:
				item.setProperty('Fanart_Image', superInfo['fanart'])
				item.setArt({'icon': superInfo['poster'], 'thumb': superInfo['poster']})
			else:
				item.setArt({'icon': control.icon, 'thumb': control.icon})
				item.setProperty('Fanart_Image', control.addonFanart())
				
			item.setInfo(type='Video', infoLabels = superInfo)
			item.addContextMenuItems(cm)
			if list != True: control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
			
		if list == True: return lists

		control.directory(syshandle, cacheToDisc=False)
	except: pass

	
def direct_downlaod(id):
	return

def openFolderx(id, meta=None):
	# meta = json.loads(meta)	
	folder = premiumizeFolder + id
	url = urlparse.urljoin(premiumize_Api, folder) 
	r = reqJson(url)
	r = r['content']
	for result in r:
		cm = []
		type = result['type']
		fileLabel = type
		id = result['id']
		name = result['name'].encode('utf-8')
		name = normalize(name)
		superInfo = {'title': name}
		playLink = '0'
		isFolder = True
		isPlayable = 'false'
		url = '%s?action=%s&id=%s' % (sysaddon, 'premiumizeOpenFolder', id)
		cm.append(('Delete from Cloud', 'RunPlugin(%s?action=premiumizeDeleteItem&id=%s&type=%s)' % (sysaddon, id, type)))
		cm.append(('Rename Item', 'RunPlugin(%s?action=realizerename&id=%s&type=%s&title=%s)' % (sysaddon, id, type, name)))
									
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
			url =  playLink
			if control.setting('downloads') == 'true': cm.append(('Download from Cloud', 'RunPlugin(%s?action=download&name=%s&url=%s)' % (sysaddon, name, url)))
		label = "[B]" + fileLabel.upper() + " |[/B] " + str(name) 
		item = control.item(label=label)
		item.setProperty('IsPlayable', isPlayable)
		item.setArt({'icon': control.icon, 'thumb': control.icon})
		item.setProperty('Fanart_Image', control.addonFanart())
		item.addContextMenuItems(cm)
		
		sysurl = client.replaceHTMLCodes(url)
		sysurl = sysurl.encode('utf-8')
		
		if meta != None and meta != '':
			if control.setting('movies.meta') != 'true': raise Exception()
			items = json.loads(str(meta))
			systitle = urllib.quote_plus(items['title'])
			superInfo = {'title': items['title'], 'genre': items['genre'], 'year': items['year'], 'poster': items['poster'], 'imdb': items['imdb'], 'fanart': items['fanart'], 'plot':items['plot'], 'rating':items['rating'], 'duration':items['duration']}
			sysmeta = urllib.quote_plus(json.dumps(superInfo))
			url = '%s?action=directPlay&url=%s&title=%s&year=%s&imdb=%s&meta=%s' % (sysaddon, playLink, systitle , items['year'], items['imdb'], sysmeta)
			item.setProperty('Fanart_Image', items['fanart'])
			
			item.setArt({'icon': items['poster'], 'thumb': items['poster']})
			
		item.setInfo(type='Video', infoLabels = superInfo)
		control.addItem(handle=syshandle, url=sysurl, listitem=item, isFolder=isFolder)
	control.content(syshandle, 'addons')
	control.directory(syshandle, cacheToDisc=True)
	
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
	cached_time, cached_results = cloudCache(mode='get')
	
	if cached_time != '0' and cached_time != None:
		if cachedSession == 'true': 
			if control.setting('first.start') == 'true':
				control.setSetting(id='first.start', value='false')
				progress.create('Scraping Your Cloud','Please Wait...')
				progress.update(100,'Scraping Your Cloud','Please Wait...')
				r = PremiumizeScraper().sources()
				cloudCache(mode='write', data=r)
			else:
				r = cached_results
		else:
			cachedLabel = "Cached Cloud: %s" % cached_time
			results = [cachedLabel, 'New Cloud Scrape', '[AUTO] Cached Cloud']
			select = control.selectDialog(results)
			if select == 0: r = cached_results
			elif select == 1: 
				progress.create('Scraping Your Cloud','Please Wait...')
				progress.update(100,'Scraping Your Cloud','Please Wait...')
				r = PremiumizeScraper().sources()
				cloudCache(mode='write', data=r)
			elif select == 2: # FORCE NEW CACHE AND AUTO CACHE MODE
				control.setSetting(id='cachecloud.remember', value='true')
				control.setSetting(id='first.start', value='false')
				progress.create('Scraping Your Cloud','Please Wait...')
				progress.update(100,'Scraping Your Cloud','Please Wait...')
				r = PremiumizeScraper().sources()
				cloudCache(mode='write', data=r)
	else:
		if cachedSession == 'true': 
			control.setSetting(id='first.start', value='false')
			progress.create('Scraping Your Cloud','Please Wait...')
			progress.update(100,'Scraping Your Cloud','Please Wait...')
			r = PremiumizeScraper().sources()
			cloudCache(mode='write', data=r)
		else:
			r = PremiumizeScraper().sources()
			cloudCache(mode='write', data=r)

		
		progress.create('Scraping Your Cloud','Please Wait...')
		progress.update(100,'Scraping Your Cloud','Please Wait...')
		
		r = PremiumizeScraper().sources()
		cloudCache(mode='write', data=r)

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
			
            data = {'type': 'torrent', "customer_id": premiumizeCustomerID, "pin": premiumizePIN}

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
			import datetime
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
			import datetime
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
	
            url = urlparse.urljoin(premiumize_Api, realizerootFolder)
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
		
