# -*- coding: utf-8 -*-

from resources.lib.modules import control
control.setSetting(id='first.start', value='true') # FORCE NEW CACHE
control.execute('RunPlugin(plugin://plugin.video.realizer/?action=service)')	
class Service():
	def __init__(self, *args):
		addonName = 'Premiumize Transfers'

	def ServiceEntryPoint(self):
		monitor = xbmc.Monitor()
		updateTime = control.setting('rss.timeout')
		updateSeconds = int(updateTime) * 3600
		

		while not monitor.abortRequested():
			if monitor.waitForAbort(updateSeconds):
                # # Abort was requested while waiting. We should exit
				break
			if control.setting('rss.1') == 'true' or control.setting('rss.2') == 'true' or control.setting('rss.3') == 'true' or control.setting('rss.4') == 'true':	
				control.execute('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')

Service().ServiceEntryPoint()			

