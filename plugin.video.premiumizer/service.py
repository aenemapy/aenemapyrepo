# -*- coding: utf-8 -*-

from resources.lib.modules import control

control.setSetting(id='first.start', value='true') # FORCE NEW CACHE
firstSetup = control.setting('first.setup')

if firstSetup != 'true': 
	from resources.lib.modules import setuptools
	newvalue = '1'

	setuptools.FirstStart()	
	control.setSetting(id='first.setup', value='true') # SETUP LIBRARY PATH IN BROWSER
	
control.execute('RunPlugin(plugin://plugin.video.premiumizer/?action=service)')	


# class Service():
    # def __init__(self, *args):
        # addonName = 'Premiumize Transfers'

    # def ServiceEntryPoint(self):
        # monitor = xbmc.Monitor()


        # while not monitor.abortRequested():
            # # check every 5 mins
            # if monitor.waitForAbort(100):
                # # Abort was requested while waiting. We should exit
                # break
				
            # control.execute('RunPlugin(plugin://plugin.video.premiumizer/?action=transferMonitor)')

# if transferMonitor !='false': Service().ServiceEntryPoint()			

