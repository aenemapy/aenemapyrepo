# -*- coding: utf-8 -*-
'''
    premiumizer Add-on
    Copyright (C) 2016 premiumizer

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


import re,sys,json,time,xbmc
import hashlib,urllib,os,zlib,base64,codecs,xmlrpclib


try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import playcount
from resources.lib.modules import favourites
from resources.lib.modules import bookmarks

inprogress_db = control.setting('inprogress_db')
progressFile = control.progressFile
dataPath = control.dataPath
import libThread


class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)


    def run(self, title, year, season, episode, imdb, tvdb, url, meta, id):
        try:
            control.sleep(200)

            # try: self.debridHandle = url['handle'].encode('utf-8')	
            # except: self.debridHandle = '0'
            # url = url['url'].encode('utf-8')
            self.seekStatus = False

            self.totalTime = 0 ; self.currentTime = 0
            self.original_meta = meta
            self.content = 'movie' if season == None or episode == None else 'episode'

            self.title = title ; self.year = year
            self.name = urllib.quote_plus(title) + urllib.quote_plus(' (%s)' % year) if self.content == 'movie' else urllib.quote_plus(title) + urllib.quote_plus(' S%02dE%02d' % (int(season), int(episode)))
            self.name = urllib.unquote_plus(self.name)
            self.season = '%01d' % int(season) if self.content == 'episode' else None
            self.episode = '%01d' % int(episode) if self.content == 'episode' else None
            # self.Nextup = None
            self.DBID = None
			
            self.FileId = id
            self.imdb = imdb if not imdb == None else '0'
            self.tvdb = tvdb if not tvdb == None else '0'

            self.metaID = [self.imdb, self.tvdb]
            self.metaID = [i for i in self.metaID if not str(i) == '0']

            poster, thumb, fanart, meta = self.getMeta(meta)

            item = control.item(path=url)
            if self.content == 'episode': item.setArt({'icon': thumb, 'thumb': fanart, 'poster': poster, 'fanart':fanart, 'tvshow.poster': poster, 'season.poster': thumb , 'tvshow.landscape':thumb})
            else: item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'fanart':thumb})

            item.setInfo(type='Video', infoLabels = meta)

            if 'plugin' in control.infoLabel('Container.PluginName'):
				control.player.play(url, item)

            control.resolve(int(sys.argv[1]), True, item)

            self.keepPlaybackAlive()

        except:
            return


    def getMeta(self, meta):
        try:
            poster = meta['poster'] if 'poster' in meta else '0'
            thumb = meta['thumb'] if 'thumb' in meta else poster
            fanart = meta['fanart'] if 'fanart' in meta else '0'
            if poster == '0': poster = control.addonPoster()

            return (poster, thumb, fanart, meta)
        except:
            pass
		
    def remove_progress_movies(self, meta):
        content = 'movies'
			
        try:
            if inprogress_db != 'true': raise Exception()
            dbcon = database.connect(progressFile)
            dbcur = dbcon.cursor()
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['imdb']))
            except: pass
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['tvdb']))
            except: pass
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['tmdb']))
            except: pass
            dbcon.commit()
        except:
            pass

    def remove_progress_episodes(self, meta):
        content = "episode"
			
        try:
            if inprogress_db != 'true': raise Exception()
            dbcon = database.connect(progressFile)
            dbcur = dbcon.cursor()
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['imdb']))
            except: pass
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['tvdb']))
            except: pass
            try: dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['tmdb']))
            except: pass
            dbcon.commit()
        except:
            pass


			
    def add_progress_movies(self, meta):
		try:
			if inprogress_db != 'true': raise Exception()
			item = dict()
			typeofcontent = 'movies'
			try: id = meta['imdb']
			except: id = meta['tvdb']
			
			if 'title' in meta: title = item['title'] = meta['title']
			if 'tvshowtitle' in meta: title = item['title'] = meta['tvshowtitle']
			if 'year' in meta: item['year'] = meta['year']
			if 'poster' in meta: item['poster'] = meta['poster']
			if 'fanart' in meta: item['fanart'] = meta['fanart']
			if 'imdb' in meta: item['imdb'] = meta['imdb']
			if 'tmdb' in meta: item['tmdb'] = meta['tmdb']
			if 'tvdb' in meta: item['tvdb'] = meta['tvdb']
			if 'tvrage' in meta: item['tvrage'] = meta['tvrage']
			if 'banner' in meta: item['banner'] = meta['banner']			
			if 'plot' in meta: item['plot'] = meta['plot']			
						

			control.makeFile(dataPath)
			dbcon = database.connect(progressFile)
			dbcur = dbcon.cursor()
			dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""id TEXT, ""items TEXT, ""UNIQUE(id)"");" % typeofcontent)
			dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (typeofcontent, id))
			dbcur.execute("INSERT INTO %s Values (?, ?)" % typeofcontent, (id, repr(item)))
			dbcon.commit()

			# control.refresh()
			# control.infoDialog('Added to Watchlist', heading=title)
		except:
			return
		
    def add_progress_episodes(self, meta):
		try:
			if inprogress_db != 'true': raise Exception()
			item = dict()
			typeofcontent = 'episode'

			id = meta['tvdb']
			
			if 'title' in meta: title = item['title'] = meta['title']
			if 'tvshowtitle' in meta: item['tvshowtitle'] = meta['tvshowtitle']
			if 'year' in meta: item['year'] = meta['year']
			if 'poster' in meta: item['poster'] = meta['poster']
			if 'fanart' in meta: item['fanart'] = meta['fanart']
			if 'imdb' in meta: item['imdb'] = meta['imdb']
			if 'tmdb' in meta: item['tmdb'] = meta['tmdb']
			if 'tvdb' in meta: item['tvdb'] = meta['tvdb']
			if 'tvrage' in meta: item['tvrage'] = meta['tvrage']
			if 'episode' in meta: item['episode'] = meta['episode']
			if 'season' in meta: item['season'] = meta['season']
			if 'premiered' in meta: item['premiered'] = meta['premiered']
			if 'original_year' in meta: item['original_year'] = meta['original_year']
			if 'banner' in meta: item['banner'] = meta['banner']			
			if 'plot' in meta: item['plot'] = meta['plot']			
					

			control.makeFile(dataPath)
			dbcon = database.connect(progressFile)
			dbcur = dbcon.cursor()
			dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""id TEXT, ""items TEXT, ""UNIQUE(id)"");" % typeofcontent)
			dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (typeofcontent, id))
			dbcur.execute("INSERT INTO %s Values (?, ?)" % typeofcontent, (id, repr(item)))
			dbcon.commit()

		except:
			return		
		
		
    def keepPlaybackAlive(self):
        self.playedOverlay = False
        for i in range(0, 240):
            if self.isPlayingVideo(): break
            xbmc.sleep(200)

        while self.isPlayingVideo():
            try:
				self.totalTime = self.getTotalTime()
				self.currentTime = self.getTime()
				setWatched =  self.currentTime / self.totalTime >= .90
				if setWatched and not self.playedOverlay == True:
					self.playedOverlay = True
					self.setPlayingOverlay()
            except:
				pass
            xbmc.sleep(2000)
			
    def setPlayingOverlay(self):
	
        try:
            if self.content == 'movie': playcount.markMovieDuringPlayback(self.imdb, '7')
            elif self.content == 'episode':playcount.markEpisodeDuringPlayback(self.imdb, self.tvdb, self.season, self.episode, '7')
        except:
            pass
        try:
            if self.DBID == None: raise Exception()

            if self.content == 'movie':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
            elif self.content == 'episode':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
               
            control.jsonrpc(rpc)
        except:
            pass
			
    def setPlayed(self):
        try:
            if control.setting('cloud.askdelete') != 'true': raise Exception()
            from resources.lib.api import premiumize
            premiumize.DeleteDialog(self.FileId)
        except:
            pass	
	
        try:
            if self.content == 'movie': playcount.markMovieDuringPlayback(self.imdb, '7')
            elif self.content == 'episode':playcount.markEpisodeDuringPlayback(self.imdb, self.tvdb, self.season, self.episode, '7')
        except:
            pass
        try:
            if self.DBID == None: raise Exception()
            if self.content == 'movie':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
            elif self.content == 'episode':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
               
            control.jsonrpc(rpc)
        except:
            pass
			
        control.refresh()
			
			
			
    def libraryProgrees(self, content, currentTime, totalTime, DBID):
        try:
			if content == 'movie': rpc = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid": %s , "resume": {"position": %s, "total": %s}}}' % (DBID, currentTime, totalTime)
			else: rpc = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid": %s , "resume": {"position": %s, "total": %s}}}' % (DBID, currentTime, totalTime)
			control.jsonrpc(rpc)
        except: pass
	

    def idleForPlayback(self):
        for i in range(0, 200):
            if control.condVisibility('Window.IsActive(busydialog)') == 1: control.idle()
            else: break
            control.sleep(100)

			
    def premiumizeClear(self):
		try: debrid.PremiumizeDelete(self.debridHandle)
		except: pass

		
    def resumePlayback(self):
        while True:
			try: # KODI 18 LEIA CHANGES TO PLAYER NOW REQUIRES isPlayingVideo to make sure Video is Playing
				if not self.isPlayingVideo(): continue 
				try: timeTotal = self.getTotalTime()
				except: timeTotal = 0
				if timeTotal != None and timeTotal != 0: break
				time.sleep(0.5)
			except:continue
        try:	
			self.offset = bookmarks.bookmarks().getPlayer(self.name)
			if self.offset != '0' and self.offset != '': self.seekTime(float(self.offset))
        except:pass
        
		
    def onPlayBackStarted(self):
        control.execute('Dialog.Close(all,true)')
        self.idleForPlayback()
		# PASSING seekStatus to Avoid Prompt Multiple Times
        if self.seekStatus == False: 
			self.seekStatus = True
			self.resumePlayback()		
			
        if control.setting('subtitles') == 'true': subtitles().get(self.name, self.imdb, self.season, self.episode)
        self.idleForPlayback()
		
    def setProgress(self):
		threads = []
		if self.currentTime == None: 
			try: self.currentTime = self.getTime()
			except: self.currentTime = 0
				
		if self.totalTime   == None: 
			try: self.totalTime = self.getTotalTime()
			except: self.totalTime = 0		

		try: self.watched  = (self.currentTime / self.totalTime >= .90)
		except: self.watched = False
		if self.watched == True: # SET 
			threads.append(libThread.Thread(self.setPlayed))
			threads.append(libThread.Thread(self.remove_progress_movies, self.original_meta))
			threads.append(libThread.Thread(bookmarks.bookmarks().delete, self.name))			
		else: 
			threads.append(libThread.Thread(bookmarks.bookmarks().reset, self.currentTime, self.totalTime, self.name))
			threads.append(libThread.Thread(self.add_progress_movies, self.original_meta))

		[i.start() for i in threads]

    def onPlayBackStopped(self):
        self.setProgress()
		
    def onPlayBackEnded(self):
        self.onPlayBackStopped()
		

	
class subtitles:
    def get(self, name, imdb, season, episode):
        try:
            if not control.setting('subtitles') == 'true': raise Exception()


            langDict = {'Afrikaans': 'afr', 'Albanian': 'alb', 'Arabic': 'ara', 'Armenian': 'arm', 'Basque': 'baq', 'Bengali': 'ben', 'Bosnian': 'bos', 'Breton': 'bre', 'Bulgarian': 'bul', 'Burmese': 'bur', 'Catalan': 'cat', 'Chinese': 'chi', 'Croatian': 'hrv', 'Czech': 'cze', 'Danish': 'dan', 'Dutch': 'dut', 'English': 'eng', 'Esperanto': 'epo', 'Estonian': 'est', 'Finnish': 'fin', 'French': 'fre', 'Galician': 'glg', 'Georgian': 'geo', 'German': 'ger', 'Greek': 'ell', 'Hebrew': 'heb', 'Hindi': 'hin', 'Hungarian': 'hun', 'Icelandic': 'ice', 'Indonesian': 'ind', 'Italian': 'ita', 'Japanese': 'jpn', 'Kazakh': 'kaz', 'Khmer': 'khm', 'Korean': 'kor', 'Latvian': 'lav', 'Lithuanian': 'lit', 'Luxembourgish': 'ltz', 'Macedonian': 'mac', 'Malay': 'may', 'Malayalam': 'mal', 'Manipuri': 'mni', 'Mongolian': 'mon', 'Montenegrin': 'mne', 'Norwegian': 'nor', 'Occitan': 'oci', 'Persian': 'per', 'Polish': 'pol', 'Portuguese': 'por,pob', 'Portuguese(Brazil)': 'pob,por', 'Romanian': 'rum', 'Russian': 'rus', 'Serbian': 'scc', 'Sinhalese': 'sin', 'Slovak': 'slo', 'Slovenian': 'slv', 'Spanish': 'spa', 'Swahili': 'swa', 'Swedish': 'swe', 'Syriac': 'syr', 'Tagalog': 'tgl', 'Tamil': 'tam', 'Telugu': 'tel', 'Thai': 'tha', 'Turkish': 'tur', 'Ukrainian': 'ukr', 'Urdu': 'urd'}

            codePageDict = {'ara': 'cp1256', 'ar': 'cp1256', 'ell': 'cp1253', 'el': 'cp1253', 'heb': 'cp1255', 'he': 'cp1255', 'tur': 'cp1254', 'tr': 'cp1254', 'rus': 'cp1251', 'ru': 'cp1251'}

            quality = ['bluray', 'hdrip', 'brrip', 'bdrip', 'dvdrip', 'webrip', 'hdtv']


            langs = []
            try:
                try: langs = langDict[control.setting('subtitles.lang.1')].split(',')
                except: langs.append(langDict[control.setting('subtitles.lang.1')])
            except: pass
            try:
                try: langs = langs + langDict[control.setting('subtitles.lang.2')].split(',')
                except: langs.append(langDict[control.setting('subtitles.lang.2')])
            except: pass

            try: subLang = xbmc.Player().getSubtitles()
            except: subLang = ''
            if subLang == langs[0]: raise Exception()

            server = xmlrpclib.Server('http://api.opensubtitles.org/xml-rpc', verbose=0)
            OSuser = control.setting('opensub.user')
            OSPass = control.setting('opensub.pw')
            token = server.LogIn(OSuser, OSPass, 'en', 'XBMC_Subtitles_v1')['token']

            sublanguageid = ','.join(langs) ; imdbid = re.sub('[^0-9]', '', imdb)

            if not (season == None or episode == None):
                result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid, 'season': season, 'episode': episode}])['data']

                fmt = ['hdtv']
            else:
                result = server.SearchSubtitles(token, [{'sublanguageid': sublanguageid, 'imdbid': imdbid}])['data']
                try: vidPath = xbmc.Player().getPlayingFile()
                except: vidPath = ''
                fmt = re.split('\.|\(|\)|\[|\]|\s|\-', vidPath)
                fmt = [i.lower() for i in fmt]
                fmt = [i for i in fmt if i in quality]

            filter = []
            result = [i for i in result if i['SubSumCD'] == '1']

            for lang in langs:
                filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in fmt)]
                filter += [i for i in result if i['SubLanguageID'] == lang and any(x in i['MovieReleaseName'].lower() for x in quality)]
                filter += [i for i in result if i['SubLanguageID'] == lang]

            try: lang = xbmc.convertLanguage(filter[0]['SubLanguageID'], xbmc.ISO_639_1)
            except: lang = filter[0]['SubLanguageID']

            content = [filter[0]['IDSubtitleFile'],]
            content = server.DownloadSubtitles(token, content)
            content = base64.b64decode(content['data'][0]['data'])
            content = str(zlib.decompressobj(16+zlib.MAX_WBITS).decompress(content))

            subtitle = xbmc.translatePath('special://temp/')
            subtitle = os.path.join(subtitle, 'TemporarySubs.%s.srt' % lang)

            codepage = codePageDict.get(lang, '')
            if codepage and control.setting('subtitles.utf') == 'true':
                try:
                    content_encoded = codecs.decode(content, codepage)
                    content = codecs.encode(content_encoded, 'utf-8')
                except:
                    pass

            file = control.openFile(subtitle, 'w')
            file.write(str(content))
            file.close()

            xbmc.sleep(1000)
            xbmc.Player().setSubtitles(subtitle)
        except:
            pass


