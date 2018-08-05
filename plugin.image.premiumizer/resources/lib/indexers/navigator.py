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


import os,sys,urlparse, xbmcaddon
import webbrowser
from resources.lib.modules import control, deviceAuthDialog


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1]) ; control.moderator()

artPath = control.artPath() ; addonFanart = control.addonFanart()

__addon__ = xbmcaddon.Addon("plugin.image.premiumizer")

class navigator:
    def root(self):

        if control.setting('premiumize.customer_id') == '' or control.setting('premiumize.customer_id') == None: 
			authDialog = deviceAuthDialog.DeviceAuthDialog('script-DeviceAuthDialog.xml', __addon__.getAddonInfo('path'), code='', url='http://premiumize.me')
			authDialog.doModal()
			del authDialog			
			sys.exit()	
		
        # self.addDirectoryItem('TEST', 'testItem', 'movies.png', 'DefaultMovies.png')
        from resources.lib.api import premiumize
        try:
			accountStatus = premiumize.info()
			self.addDirectoryItem(accountStatus, '0', 'search.png', 'DefaultMovies.png')
        except:pass
        if control.setting('premiumize.customer_id') == '' or control.setting('premiumize.customer_id') == None: 
				authDialog = deviceAuthDialog.DeviceAuthDialog('script-DeviceAuthDialog.xml', __addon__.getAddonInfo('path'), code='test code', url='http://premiumize.me')
				authDialog.doModal()
				del authDialog			
				control.openSettings('0.0')
			
        else:
			self.addDirectoryItem(50002, 'premiumizerootFolder', 'cloud.png', 'DefaultMovies.png')
			self.addDirectoryItem(50003, 'premiumizeTransfers', 'cloud.png', 'DefaultMovies.png')
			self.addDirectoryItem(50004, 'premiumizeAdd', 'cloud.png', 'DefaultMovies.png')

        self.endDirectory()

    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')

        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.png', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.png', 'DefaultTVShows.png', isAction=False)

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
        item.setArt({'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=False)


