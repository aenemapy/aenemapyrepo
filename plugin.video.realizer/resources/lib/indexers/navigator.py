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


import os,sys,urlparse, xbmcaddon
import webbrowser
from resources.lib.modules import control, deviceAuthDialog
from resources.lib.api import trakt, debrid

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1]) ; control.moderator()

artPath = control.artPath() ; addonFanart = control.addonFanart()

imdbCredentials = False if control.setting('imdb.user') == '' else True

traktCredentials = trakt.getTraktCredentialsInfo()

traktIndicators = trakt.getTraktIndicatorsInfo()

queueMenu = control.lang(32065).encode('utf-8')

__addon__ = xbmcaddon.Addon()
class navigator:
    def root(self):
        status = debrid.realdebrid().accountInfo()
		
        if status != True: 
			authDialog = deviceAuthDialog.DeviceAuthDialog('script-DeviceAuthDialog.xml', __addon__.getAddonInfo('path'), code='', url='http://real-debrid.com/?id=915002')
			authDialog.doModal()
			del authDialog			
			sys.exit()	
		
        #self.addDirectoryItem('TEST', 'testItem', 'movies.png', 'DefaultMovies.png')
        self.addDirectoryItem(50001, 'rdNavigator', 'cloud.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Lists', 'browse_nav', 'cloud.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Download Manager', 'download_manager', 'cloud.png', 'DefaultAddonProgram.png')   
        self.addDirectoryItem('RSS Manager', 'rss_manager', 'cloud.png', 'DefaultAddonProgram.png')		
        self.addDirectoryItem(32008, 'toolNavigator', 'settings.png', 'DefaultAddonProgram.png')
        self.endDirectory()
		
    def download_manager(self):
        self.addDirectoryItem('Downloading', 'download_manager_list', 'cloud.png', 'DefaultFolder.png')
        downloads = True if control.setting('downloads') == 'true' else False
        if downloads == True:
			download_path = control.setting('download.path')
			dest = control.transPath(download_path)
			if len(control.listDir(dest)[0]) > 0:
				self.addDirectoryItem(32009, dest, 'cloud.png', 'DefaultFolder.png', isAction=False)	
        self.endDirectory()
		

		

    def browse_nav(self, lite=False):
        self.addDirectoryItem(32001, 'movieNavigator', 'movies.png', 'DefaultMovies.png')
        self.addDirectoryItem(32002, 'tvNavigator', 'tv.png', 'DefaultTVShows.png')	
        self.endDirectory()		
		
		
    def movies(self, lite=False):
        self.addDirectoryItem(40000, 'moviesInProgress', 'movies.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('New HD Releases', 'movies&url=newreleases', 'movies.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32017, 'movies&url=trending', 'movies.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(40009, 'movieFavourites', 'mymovies.png', 'DefaultMovies.png')
        if traktCredentials == True: self.addDirectoryItem('Trakt on Deck', 'traktOnDeck&content=movies', 'trakt.png', 'DefaultMovies.png', queue=True)		
        if traktCredentials == True and imdbCredentials == True:

            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32034, 'movies&url=imdbwatchlist','imdb.png', 'DefaultMovies.png', queue=True)

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=traktfeatured', 'trakt.png', 'DefaultMovies.png', queue=True)

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'DefaultMovies.png', queue=True)

        self.addDirectoryItem(32039, 'movieUserlists', 'mymovies.png', 'DefaultMovies.png')

        self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'DefaultMovies.png')
        self.endDirectory()

		
    def rdNav(self):
        status = debrid.realdebrid().accountInfo()
		
        if status != True: 
			authDialog = deviceAuthDialog.DeviceAuthDialog('script-DeviceAuthDialog.xml', __addon__.getAddonInfo('path'), code='', url='http://real-debrid.com/?id=915002')
			authDialog.doModal()
			del authDialog			
			sys.exit()	
			
        else:
			self.addDirectoryItem(50002, 'rdTorrentList&page=1', 'cloud.png', 'DefaultMovies.png')
			self.addDirectoryItem(50003, 'rdTransfers&page=1', 'cloud.png', 'DefaultMovies.png')

        self.endDirectory()

    def library(self):
        self.addDirectoryItem('Force Cloud Sync', 'forcecloudsync', 'cloud.png', 'DefaultMovies.png', isFolder=False)
        self.addDirectoryItem('Selective Cloud to Library Manager', 'selectivelibrary_nav', 'cloud.png', 'DefaultMovies.png', isFolder=True)
        self.endDirectory()
		
    def mymovies(self, lite=False):
        self.addDirectoryItem(40009, 'movieFavourites', 'mymovies.png', 'DefaultMovies.png')

        if traktCredentials == True and imdbCredentials == True:
	
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32034, 'movies&url=imdbwatchlist','imdb.png', 'DefaultMovies.png', queue=True)

        elif traktCredentials == True:
            self.addDirectoryItem('Trakt on Deck', 'traktOnDeck&content=movies', 'trakt.png', 'DefaultMovies.png', queue=True)		
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktCredentials == True:
            self.addDirectoryItem('Trakt on Deck', 'traktOnDeck&content=movies', 'trakt.png', 'DefaultMovies.png', queue=True)	
            self.addDirectoryItem(32035, 'movies&url=traktfeatured', 'trakt.png', 'DefaultMovies.png', queue=True)

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'DefaultMovies.png', queue=True)

        self.addDirectoryItem(32039, 'movieUserlists', 'mymovies.png', 'DefaultMovies.png')


        self.endDirectory()


    def tvshows(self, lite=False):
        self.addDirectoryItem(32006, 'calendar&url=added', 'tv.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)
        self.addDirectoryItem(32017, 'tvshows&url=trending', 'tv.png', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem('MY Watchlist', 'tvFavourites', 'mymovies.png', 'DefaultMovies.png')   
        if traktCredentials == True:
            self.addDirectoryItem('Trakt On Deck', 'calendar&url=traktOnDeck', 'trakt.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32035, 'tvshows&url=traktfeatured', 'trakt.png', 'DefaultTVShows.png')

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=trending', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'DefaultTVShows.png', queue=True)
            self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)
            self.addDirectoryItem(32038, 'calendar&url=mycalendar', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        self.addDirectoryItem(32040, 'tvUserlists', 'mytv.png', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32041, 'episodeUserlists', 'trakt.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32010, 'tvSearchTvdb', 'search.png', 'DefaultTVShows.png')
        self.endDirectory()


    def mytvshows(self, lite=False):
        # self.accountCheck()
        self.addDirectoryItem('MY Watchlist', 'tvFavourites', 'mymovies.png', 'DefaultMovies.png')   
        if traktCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32035, 'tvshows&url=traktfeatured', 'trakt.png', 'DefaultTVShows.png')

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=trending', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'DefaultTVShows.png', queue=True)
            self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)
            self.addDirectoryItem(32038, 'calendar&url=mycalendar', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        self.addDirectoryItem(32040, 'tvUserlists', 'mytv.png', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32041, 'episodeUserlists', 'trakt.png', 'DefaultTVShows.png')

        # if lite == False:
            # self.addDirectoryItem(32031, 'tvliteNavigator', 'tvshows.png', 'DefaultTVShows.png')
            # self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
            # self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'DefaultTVShows.png')

        self.endDirectory()


    def tools(self):

        self.addDirectoryItem(32043, 'openSettings&query=0.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32044, 'openSettings&query=1.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32048, 'openSettings&query=2.0', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(40005, 'openSettings&query=3.0', 'settings.png', 'DefaultAddonProgram.png')

        #self.addDirectoryItem(32052, 'clearCache', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]SETTINGS:[/B] Clear Cache/Meta', 'clearMeta', 'settings.png', 'DefaultAddonProgram.png')

        self.addDirectoryItem(40006, 'backupSettings', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(40007, 'restoreSettings', 'settings.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]HELP[/B]', 'helpNavigator', 'help.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('[B]CHANGELOG[/B]', 'changelogNavigator', 'help.png', 'DefaultAddonProgram.png')		
        self.endDirectory()

    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')

        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.png', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.png', 'DefaultTVShows.png', isAction=False)

        self.endDirectory()


    def search(self):
        self.addDirectoryItem(32001, 'movieSearch', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32002, 'tvSearch', 'search.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32029, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32030, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')

        self.endDirectory()


    def accountCheck(self):
        if traktCredentials == False and imdbCredentials == False:
            control.idle()
            control.infoDialog(control.lang(32042).encode('utf-8'), sound=True, icon='WARNING')
            sys.exit()


    def clearCache(self):
        control.idle()
        from resources.lib.modules import cache
        cache.cache_clear()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')


    def help(self):
		import xbmc,xbmcgui,xbmcaddon,xbmcvfs,os
		addonInfo = xbmcaddon.Addon().getAddonInfo
		addonPath = xbmc.translatePath(addonInfo('path'))
		changelogfile = os.path.join(addonPath, 'help.txt')
		r = open(changelogfile)
		text = r.read()

		id = 10147
		xbmc.executebuiltin('ActivateWindow(%d)' % id)
		xbmc.sleep(500)
		win = xbmcgui.Window(id)
		retry = 50
		while (retry > 0):
			try:
				xbmc.sleep(10)
				retry -= 1
				win.getControl(1).setLabel('Version: %s' %(xbmcaddon.Addon().getAddonInfo('version')))
				win.getControl(5).setText(text)
				return
			except:
				pass
				
    def changelog(self):
		import xbmc,xbmcgui,xbmcaddon,xbmcvfs,os
		addonInfo = xbmcaddon.Addon().getAddonInfo
		addonPath = xbmc.translatePath(addonInfo('path'))
		changelogfile = os.path.join(addonPath, 'changelog.txt')
		r = open(changelogfile)
		text = r.read()

		id = 10147
		xbmc.executebuiltin('ActivateWindow(%d)' % id)
		xbmc.sleep(500)
		win = xbmcgui.Window(id)
		retry = 50
		while (retry > 0):
			try:
				xbmc.sleep(10)
				retry -= 1
				win.getControl(1).setLabel('Version: %s' %(xbmcaddon.Addon().getAddonInfo('version')))
				win.getControl(5).setText(text)
				return
			except:
				pass
		
		
		
    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
		
        thumb = control.getIcon(thumb)

        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


