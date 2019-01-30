# -*- coding: utf-8 -*-

from resources.lib.modules import control
control.setSetting(id='first.start', value='true') # FORCE NEW CACHE
control.execute('RunPlugin(plugin://plugin.video.realizer/?action=service)')	
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
				
            # control.execute('RunPlugin(plugin://plugin.video.realizer/?action=transferMonitor)')

# if transferMonitor !='false': Service().ServiceEntryPoint()			

