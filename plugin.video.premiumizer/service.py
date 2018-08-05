# -*- coding: utf-8 -*-

from resources.lib.modules import control
from resources.lib.modules import updater

updateService = control.setting('library.update')
transferMonitor = control.setting('transfer.monitor')
control.setSetting(id='cachecloud.remember', value='false')

if updateService != 'false': 
	print ("UPDATER SERVICE STARTED")
	control.execute('RunPlugin(plugin://plugin.video.premiumizer/?action=service)')

class Service():
    def __init__(self, *args):
        addonName = 'Premiumize Transfers'

    def ServiceEntryPoint(self):
        monitor = xbmc.Monitor()


        while not monitor.abortRequested():
            # check every 5 mins
            if monitor.waitForAbort(300):
                # Abort was requested while waiting. We should exit
                break
				
            control.execute('RunPlugin(plugin://plugin.video.premiumizer/?action=transferMonitor)')

if transferMonitor !='false': Service().ServiceEntryPoint()			

