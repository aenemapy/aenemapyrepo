# -*- coding: utf-8 -*-

'''
    hideosd Add-on
    Copyright (C) 2018 aenema

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see .
'''

import xbmc,xbmcaddon
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])
addonInfo = xbmcaddon.Addon().getAddonInfo
settings = xbmcaddon.Addon().getSetting
profilePath = xbmc.translatePath(addonInfo('profile'))
addonPath = xbmc.translatePath(addonInfo('path'))
hideTimeout = settings('hide.timeout')
enableHide  = settings('hide.enable')

class Service():
    def __init__(self, *args):
        addonName = 'Auto Hide Video OSD'
        self.skipped = False

    def ServiceEntryPoint(self):
        monitor = xbmc.Monitor()


        while not monitor.abortRequested():
            # check every 5 sec
            if monitor.waitForAbort(1):
                # Abort was requested while waiting. We should exit
                break
            if xbmc.Player().isPlaying():
                try:
                    if enableHide == 'true': CHECK_OSD()
                except:pass
            else: self.skipped = False
                
def CHECK_OSD():
    seconds = str(settings('hide.timeout'))
    if xbmc.getCondVisibility("Window.IsActive(videoosd)"):
        window = "videoosd"
        if seconds and seconds != "0":
            while xbmc.getCondVisibility("Window.IsActive(%s)" % window):
                if xbmc.getCondVisibility("System.IdleTime(%s)" % seconds): xbmc.executebuiltin("Dialog.Close(%s)" % window)
                else: xbmc.sleep(500)   

Service().ServiceEntryPoint()
