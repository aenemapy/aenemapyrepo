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



class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)


    def run(self, title, url, xbmc_id, content):
        try:
            control.sleep(200)

            self.content = 'movie' if content == 'movie' else 'episode'

            self.title = title
            self.DBID = xbmc_id
			
            self.imdb = ''
			
            self.name =  cleantitle.get(title) + str(self.DBID)
			
            #print ("PREMIUMIZE PLAYER", self.title, self.DBID, self.content, url)

            poster, thumb, fanart, meta = self.getMeta()
			
            #print ("PREMIUMIZE PLAYER 2", url, self.title, self.DBID, poster, thumb, fanart, meta)
            if self.content == 'movie': self.ids = {'imdb': self.imdb}
            else: self.ids = {'imdb': self.imdb, 'tvdb': self.imdb }
            self.ids = dict((k,v) for k, v in self.ids.iteritems() if not v == '0')
			
            item = control.item(path=url)
			
            item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'fanart':thumb})

            item.setInfo(type='Video', infoLabels = meta)

            control.resolve(int(sys.argv[1]), True, item)
            control.window.setProperty('script.trakt.ids', json.dumps(self.ids))
            self.keepPlaybackAlive()
            control.window.clearProperty('script.trakt.ids')
        except:
            return


    def getMeta(self):
        try:
            if self.content != 'movie': raise Exception()
            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties" : ["imdbnumber" , "fanart", "title", "originaltitle", "rating", "genre", "year", "director", "plot", "thumbnail"]}, "id": 1}')
            meta = unicode(lib, 'utf-8', errors='ignore')
            meta = json.loads(meta)['result']['movies']

            meta = [i for i in meta if str(i['movieid']) == str(self.DBID)][0]
            #print ("PREMIUMIZE PLAYER META", meta)
            self.imdb = meta['imdbnumber']
            poster = thumb = fanart = meta['thumbnail']
            
			# PASS POSTER AND FANART FOR INPROGRESS DATABASES"
            if "fanart" in meta: fanart = meta['fanart']
            meta['poster'] = poster

            for k, v in meta.iteritems():
                if type(v) == list:
                    try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
                    except: meta[k] = ''
                else:
                    try: meta[k] = str(v.encode('utf-8'))
                    except: meta[k] = str(v)			
			
            return (poster, thumb, fanart, meta)
        except:
            pass
			
        try:
            if self.content != 'episode': raise Exception()
            #print ("PREMIUMIZE PLAYER META EPISODES")
            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"properties" : ["tvshowid", "title", "originaltitle", "season", "episode", "plot", "thumbnail", "art", "file"]}, "id": 1}')
            meta = unicode(lib, 'utf-8', errors='ignore')
            meta = json.loads(meta)['result']['episodes']
            #print ("PREMIUMIZE PLAYER META", meta)

            meta = [i for i in meta if str(i['episodeid']) == str(self.DBID)][0]
            tvshowid = meta['tvshowid']
            poster = thumb = fanart = meta['thumbnail']
            
            if "fanart" in meta: fanart = meta['fanart']
            meta['poster'] = poster

            for k, v in meta.iteritems():
                if type(v) == list:
                    try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
                    except: meta[k] = ''
                else:
                    try: meta[k] = str(v.encode('utf-8'))
                    except: meta[k] = str(v)			
			
            try:
				rpc_file = {"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["title", "imdbnumber"]}, "id": "1"}
				rpc_file = json.dumps(rpc_file)
				result_file = xbmc.executeJSONRPC(rpc_file)	
				result_file = json.loads(result_file)	
								
				result_file = result_file['result']['tvshows']
				result_meta = [i for i in result_file if str(i['tvshowid']) == str(tvshowid)][0]
		
				self.imdb   = result_meta['imdbnumber']
				meta['tvshowtitle'] = result_meta['title']
				
            except:pass
			
            return (poster, thumb, fanart, meta)
        except:
            pass
        
        # self.Nextup = {'tvshowid', tvshowid, 'episodeid': self.DBID }
        poster, thumb, fanart, meta = '', '', '', {'title': self.title}
        return (poster, thumb, fanart, meta)
		
	
    def keepPlaybackAlive(self):
        self.playedOverlay = False
        for i in range(0, 240):
            if self.isPlayingVideo(): break
            xbmc.sleep(200)

        while self.isPlayingVideo():
            try:
				self.totalTime = self.getTotalTime()
				self.currentTime = self.getTime()
				self.setWatched =  self.currentTime / self.totalTime >= .90
				if self.setWatched and not self.playedOverlay == True:
					self.playedOverlay = True
					self.setPlayingOverlay()
            except:
				pass
            xbmc.sleep(1000)
			
    def setPlayingOverlay(self):
        try:
            if self.DBID == None: raise Exception()

            if self.content == 'movie':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
            elif self.content == 'episode':
                rpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID)
               
            control.jsonrpc(rpc)
        except:
            pass

			
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

    def onPlayBackStarted(self):
        control.execute('Dialog.Close(all,true)')
        self.idleForPlayback()
        self.setProgress()		

		
    def setProgress(self):
        while True:
			try:
				if not self.isPlayingVideo(): continue 
				try: timeTotal = self.getTotalTime()
				except: timeTotal = 0
				if timeTotal != None and timeTotal != 0: break
				time.sleep(0.5)
			except:continue
        progress = 0

        self.offset = bookmarks.bookmarks().getPlayer(self.name)
        if not self.offset == '0': self.seekTime(float(self.offset))
			

    def onPlayBackStopped(self):
		bookmarks.bookmarks().reset(self.currentTime, self.totalTime, self.name)

    def onPlayBackEnded(self):
        self.onPlayBackStopped()
	

