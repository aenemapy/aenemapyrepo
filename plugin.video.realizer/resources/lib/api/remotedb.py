# -*- coding: utf-8 -*-

'''
    realizer Add-on
    Copyright (C) 2016 realizer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,json,urlparse,time,urllib,sys,xbmc

from resources.lib.modules import utils

from resources.lib.modules import control
from resources.lib.api import trakt
from resources.lib.modules import client
from resources.lib.modules import playcount
from resources.lib.modules.log_utils import debug
import requests

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action = params.get('action')



addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

traktCredentials = trakt.getTraktCredentialsInfo()

DBURL = control.setting('remotedb.url')

def manager(imdb, tmdbtvdb, meta, content):
    try:
        if DBURL == None or DBURL == '': 
			control.infoDialog('RemoteDB Address is Empty...', time=3000)
			return
        HOSTDB = str(DBURL)
        DBLINK = str(HOSTDB) + "/library.php?action=%s"
        # print("DATABASE REMOTE", DBLINK)		
        if imdb == '' or imdb == '0' or imdb == None: raise Exception()
		
        actions = ['Add to Library', 'Remove from Library']
        meta = json.loads(meta)
        dbname = meta['title'].encode('utf-8') if 'title' in meta else '0'
        # print("DATABASE REMOTE", dbname)
        dbposter = meta['poster'].encode('utf-8') if 'poster' in meta else '0'
        # print("DATABASE REMOTE", dbposter)		
        dbfanart = meta['fanart'].encode('utf-8') if 'fanart' in meta else '0'
        # print("DATABASE REMOTE", dbfanart)
        dbyear = meta['year'].encode('utf-8') if 'year' in meta else '0'
        # print("DATABASE REMOTE", dbyear)
        dbrating = meta['rating'].encode('utf-8') if 'rating' in meta else '0'
        # print("DATABASE REMOTE", dbrating)
        dbgenre = meta['genre'].encode('utf-8') if 'genre' in meta else '0'
        # print("DATABASE REMOTE", dbgenre)
        dbplot = meta['plot'].encode('utf-8') if 'plot' in meta else '0'		
        # print("DATABASE REMOTE", dbplot)				
        payload = {'title':dbname, 'imdb':imdb, 'tmdbtvdb': tmdbtvdb, 'poster':dbposter, 'fanart':dbfanart, 'year':dbyear, 'rating':dbrating, 'genre':dbgenre, 'plot':dbplot}
		
        # print ("DATABASE PAYLOAD", payload)
        select = control.selectDialog(actions, 'Remote Library Manager')
        if tmdbtvdb == '0' or tmdbtvdb == None or tmdbtvdb == '': tmdbtvdb = imdb
        if select == -1:
            return
        elif select == 0: 
			if content == 'movie': 
				dbcheck = DBLINK % 'movies'
				check = requests.get(dbcheck).content
				if imdb in check or tmdbtvdb in check: 
					control.infoDialog('Item already in Library', heading=str(dbname), sound=True)
					return
				act = 'addmovie'
			else: 
				dbcheck = DBLINK % 'tv'
				check = requests.get(dbcheck).content
				if imdb in check or tmdbtvdb in check: 
					control.infoDialog('Item already in Library', heading=str(dbname), sound=True)
					return
				act = 'addtv'			

			url = DBLINK % act
			r = requests.post(url, data=payload).content
			
        elif select == 1: 
			
			if content == 'movie': 

				dbcheck = DBLINK % 'movies'
				check = requests.get(dbcheck).content
				
				if not str(imdb) in check: 
					control.infoDialog('Item Not in Library', heading=str(dbname), sound=True)
					return			
				if not str(tmdbtvdb) in check: 
					control.infoDialog('Item Not in Library', heading=str(dbname), sound=True)
					return
			
				act = 'deletemovie'
			else: 

				dbcheck = DBLINK % 'tv'
				check = requests.get(dbcheck).content
				if not str(imdb) in check: 
					control.infoDialog('Item Not in Library', heading=str(dbname), sound=True)
					return			
				if not str(tmdbtvdb) in check: 
					control.infoDialog('Item Not in Library', heading=str(dbname), sound=True)
					return
	
				act = 'deletetv'			
			
			url = DBLINK % act
			r = requests.post(url, data=payload).content
        icon = control.infoLabel('ListItem.Icon') if not r == None else 'ERROR'

        control.infoDialog(r, heading=str(dbname), sound=True, icon=icon)
        if act == 'deletemovie' or act == 'deletetv': control.refresh()
    except:
        return

def getMovies(query=None):
	if DBURL == None or DBURL == '': 
		control.infoDialog('RemoteDB Address is Empty...', time=3000)
		return
	DBlist = []
	HOSTDB = str(DBURL)
	DBLINK = str(HOSTDB) + "/library.php?action=movies"
	r = requests.get(DBLINK).json()
	for item in r:
		try:
			title = item['title'].encode('utf-8')
			imdb = item['imdb'].encode('utf-8')
			tmdb = item['tmdbtvdb'].encode('utf-8') 
			year = item['year'].encode('utf-8') if 'year' in item else '0'
			poster = item['poster'].encode('utf-8') if 'poster' in item else addonPoster
			fanart = item['fanart'].encode('utf-8') if 'rating' in item else addonFanart
			rating = item['rating'].encode('utf-8') if 'rating' in item else '0'
			genre = item['genre'].encode('utf-8') if 'genre' in item else '0'
			plot = item['plot'].encode('utf-8') if 'plot' in item else '0'
									
			# print("REMOTEDB items", title, imdb, tmdb, year, poster, fanart, rating, genre, plot)			
			DBlist.append({'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb,'poster': poster , 'fanart': fanart, 'rating':rating, 'genre': genre, 'plot': plot})
		except:pass
	DBlist = sorted(DBlist, key=lambda k: utils.title_key(k['title']))
	if query == None or query == '': movieDirectory(DBlist)	
	else: return DBlist

def moviesToLibrary():
	if DBURL == None or DBURL == '': 
		control.infoDialog('RemoteDB Address is Empty...', time=3000)
		return
	from resources.lib.modules import libtools
	DBlist = getMovies(query='list')
	control.infoDialog('RemoteDB Movies To Library in Progress...', time=3000)
	for item in DBlist:
		try:
			title = item['title'].encode('utf-8')
			imdb = item['imdb'].encode('utf-8')
			if imdb == '0': continue
			tmdb = item['tmdb'].encode('utf-8') 
			year = item['year'].encode('utf-8') if 'year' in item else '0'
			poster = item['poster'].encode('utf-8') if 'poster' in item else addonPoster
			libtools.libmovies().add(title, title, year, imdb, tmdb, icon=poster)
		except:pass			
			# print("REMOTEDB items", title, imdb, tmdb, year, poster, fanart, rating, genre, plot)			
			
def tvToLibrary():
	if DBURL == None or DBURL == '': 
		control.infoDialog('RemoteDB Address is Empty...', time=3000)
		return
	from resources.lib.modules import libtools
	DBlist = getTV(query='list')
	control.infoDialog('RemoteDB Tv To Library in Progress...', time=3000)
	for item in DBlist:
		try:
			title = item['title'].encode('utf-8')
			imdb = item['imdb'].encode('utf-8')
			tvdb = item['tvdb'].encode('utf-8') 
			year = item['year'].encode('utf-8') if 'year' in item else '0'
			poster = item['poster'].encode('utf-8') if 'poster' in item else addonPoster
			libtools.libtvshows().add(title, year, imdb, tvdb, icon=poster)
		except:pass	

def getTV(query=None):
	if DBURL == None or DBURL == '': 
		control.infoDialog('RemoteDB Address is Empty...', time=3000)
		return
	DBlist = []
	HOSTDB = str(DBURL)
	DBLINK = str(HOSTDB) + "/library.php?action=tv"
	r = requests.get(DBLINK).json()
	print ("TV REMOTE LIST 1", query, r)
	for item in r:
		try:
			title = item['title'].encode('utf-8')
			imdb = item['imdb'].encode('utf-8')
			tvdb = item['tmdbtvdb'].encode('utf-8') 
			year = item['year'].encode('utf-8') if 'year' in item else '0'
			poster = item['poster'].encode('utf-8') if 'poster' in item else addonPoster
			fanart = item['fanart'].encode('utf-8') if 'rating' in item else addonFanart
			rating = item['rating'].encode('utf-8') if 'rating' in item else '0'
			genre = item['genre'].encode('utf-8') if 'genre' in item else '0'
			plot = item['plot'].encode('utf-8') if 'plot' in item else '0'
									
			DBlist.append({'title': title, 'tvshowtitle': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb,'poster': poster , 'fanart': fanart, 'rating':rating, 'genre': genre, 'plot': plot})
		except:pass
	print ("TV REMOTE LIST 2", DBlist)
	DBlist = sorted(DBlist, key=lambda k: utils.title_key(k['title']))
	print ("TV REMOTE LIST 3", DBlist)
	if query == None or query == '': tvDirectory(DBlist)	
	else: return DBlist	
	
def movieDirectory(items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getMovieIndicators(refresh=True) if action == 'movies' else playcount.getMovieIndicators()

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        watchedMenu = control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')
		
        remoteManagerMenu = 'Remote Library'

        nextMenu = control.lang(32053).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                label = '%s' % (i['title'])
                imdb, tmdb, title, year = i['imdb'], i['tmdb'], i['originaltitle'], i['year']
                sysname = urllib.quote_plus('%s (%s)' % (title, year))
                systitle = urllib.quote_plus(title)

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tmdb_id': tmdb})
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                #meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not 'duration' in i: meta.update({'duration': '120'})
                elif i['duration'] == '0': meta.update({'duration': '120'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                poster = [i[x] for x in ['poster3', 'poster', 'poster2'] if i.get(x, '0') != '0']
                poster = poster[0] if poster else addonPoster
                meta.update({'poster': poster})
                print ("MOVIE DIRECTORY META", meta)
                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, sysmeta)
                sysurl = urllib.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)

                print ("MOVIE DIRECTORY 2", i)
                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append(('Marks As Unwatched', 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append(('Marks As Watched', 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                cm.append((remoteManagerMenu, 'RunPlugin(%s?action=remoteManager&imdb=%s&tmdb=%s&meta=%s&content=movie)' % (sysaddon, imdb, tmdb, sysmeta)))

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (sysaddon, sysname, imdb)))

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s&icon=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb, poster)))

                item = control.item(label=label)

                art = {}
                art.update({'icon': poster, 'thumb': poster, 'poster': poster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})


                if settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                    item.setProperty('Fanart_Image', i['fanart2'])
                elif settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)
                print ("MOVIE DIRECTORY 4", i)
                item.setArt(art)
                print ("MOVIE DIRECTORY 5", i)				
                item.addContextMenuItems(cm)
                print ("MOVIE DIRECTORY 6", i)
                item.setProperty('IsPlayable', isPlayable)
                print ("MOVIE DIRECTORY 7", meta)
                item.setInfo(type='Video', infoLabels = meta)
                print ("MOVIE DIRECTORY 8", i)
                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)
                print ("MOVIE DIRECTORY FINAL", i)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)

def tvDirectory(items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        indicators = playcount.getTVShowIndicators(refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

        flatten = True if control.setting('flatten.tvshows') == 'true' else False

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        nextMenu = control.lang(32053).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')
		
        remoteManagerMenu = 'Remote Library'
		

        for i in items:
            try:
                label = i['title']
                systitle = sysname = urllib.quote_plus(i['originaltitle'])
                sysimage = urllib.quote_plus(i['poster'])
                imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tvdb_id': tvdb})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tvdb))
					
                    # print ("realizer OVERLAY", label, overlay)
                    if overlay == 7: meta.update({'playcount': 1, 'overlay': 7})
                    else: meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                sysmeta = urllib.quote_plus(json.dumps(meta))
                if flatten == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)
                else:
                    url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, sysmeta)


                cm = []

                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=season&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (sysaddon, urllib.quote_plus(systitle), urllib.quote_plus(year), urllib.quote_plus(imdb), urllib.quote_plus(tvdb))))

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&query=7)' % (sysaddon, systitle, imdb, tvdb)))

                cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&query=6)' % (sysaddon, systitle, imdb, tvdb)))

                cm.append((remoteManagerMenu, 'RunPlugin(%s?action=remoteManager&imdb=%s&tvdb=%s&meta=%s&content=tv)' % (sysaddon, imdb, tvdb, sysmeta)))

                if not action == 'tvFavourites':cm.append(('Add to Watchlist', 'RunPlugin(%s?action=addFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))
                if action == 'tvFavourites': cm.append(('Remove From Watchlist', 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))

                # if not action == 'tvdbFav':cm.append(('Add To Tvdb', 'RunPlugin(%s?action=tvdbAdd&tvshowtitle=%s&tvdb=%s)' % (sysaddon, systitle, tvdb)))
                # if action == 'tvdbFav': cm.append(('Remove From Tvdb', 'RunPlugin(%s?action=tvdbRemove&tvdb=%s)' % (sysaddon, tvdb)))
				
				
                
				
                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&icon=%s)' % (sysaddon, systitle, year, imdb, tvdb, i['poster'])))

                item = control.item(label=label)

                art = {}

                if 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                #elif 'poster2' in i and not i['poster2'] == '0':
                    #art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                #elif 'banner2' in i and not i['banner2'] == '0':
                    #art.update({'banner': i['banner2']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                #elif settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                    #item.setProperty('Fanart_Image', i['fanart2'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setInfo(type='Video', infoLabels = meta)

                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'tvshows')
        control.directory(syshandle, cacheToDisc=True)
		
def escapeDB(title):
	title = re.sub('"', '\\"', title)
	title = re.sub("'", "\\'", title)
	title = re.sub(":", "\\:", title)
	title = re.sub(",", "\\,", title)
	title = re.sub("_", "", title)
	return title			

def unescapeDB(title):
	title = re.sub("\\", "", title)
	return title	



def dbMoviePlaycount(id, type):
	print ("MOVIEPLAYCOUNT 2", id, type)
	# req = DBURL + '/library.php?action=movieprogress'
	# r = requests.get(req).json()
	if type == '7':  
		req = DBURL + '/library.php?action=addmovieprogress&imdb=%s&tmdb=%s' % (id, '0')
		r = requests.get(req).content
		
	elif type =='6': 
		req = DBURL + '/library.php?action=deletemovieprogress&imdb=%s&tmdb=%s' % (id, '0')
		r = requests.get(req).content
		
	elif type == 'list': 
		req = DBURL + '/library.php?action=movieprogress'
		r = requests.get(req).json()
		if id in r: return '1'
		else: return '0'
	
		
	
