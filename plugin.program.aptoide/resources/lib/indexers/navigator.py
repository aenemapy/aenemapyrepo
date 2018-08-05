# -*- coding: utf-8 -*-

'''
    aptoide Add-on
    Copyright (C) 2016 aptoide

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


import os,sys,urlparse,xbmcgui

from resources.lib.modules import control

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1]) ; control.moderator()

artPath = control.artPath() ; addonFanart = control.addonFanart()
dialog = xbmcgui.Dialog()
class navigator:
    def root(self):
        self.checkSettings()

        self.addDirectoryItem('Most Popular', 'most_populars', 'icon.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Games', 'getGames', 'icon.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Applications', 'getApplications', 'icon.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Search', 'searchApp', 'icon.png', 'DefaultAddonProgram.png')
        self.endDirectory()

		
    def checkSettings(self):
		from resources.lib.modules import control
		if control.setting('download.path') == '': 
			dialog.ok('Aptoide','Please Setup a Download Location First...','','')
			control.openSettings('0.0')		

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


