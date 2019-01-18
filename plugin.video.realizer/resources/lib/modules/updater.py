# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

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


import json, xbmc,xbmcgui,os,zipfile,xbmcaddon,re,sys
import requests
from resources.lib.modules import control, downloadzip, extract
addonIcon = control.addonIcon()
addonInfo = xbmcaddon.Addon().getAddonInfo
addonVersion = str(addonInfo('version'))
dialog = xbmcgui.Dialog()
    
realizerPath = xbmc.translatePath(os.path.join('special://home/userdata/realizer_updates',''))
if not os.path.exists(realizerPath): os.makedirs(realizerPath)
  
def updatelibrary():
	# try:
		# refresh = control.setting('library.refresh')
		# refresh = (re.sub('[^0-9]', '', refresh)) 
		# if refresh == '' or refresh == None: refresh = '0'
		# #print ("LIBRARY REFRESH", refresh)
		# from datetime import datetime
		# timeNow =  datetime.now().strftime('%Y%m%d')
		# timeNow = (re.sub('[^0-9]', '',timeNow)) 
		# #print ("LIBRARY REFRESH", timeNow)
		# if str(timeNow) == str(refresh): raise Exception()
		# control.setSetting(id='library.refresh', value=timeNow)
		# try:
			# libraryPath = xbmc.translatePath(control.setting('library.path'))
			# if control.setting('library.deleteold') != 'true': raise Exception()
			# try: shutil.rmtree(libraryPath)
			# except:pass
			# for root, dirs, files in os.walk(libraryPath , topdown=True):
				# dirs[:] = [d for d in dirs]
				# for name in files:
					# try:
						# os.remove(os.path.join(root,name))
						# os.rmdir(os.path.join(root,name))
					# except: pass
							
				# for name in dirs:
					# try: os.rmdir(os.path.join(root,name)); os.rmdir(root)
					# except: pass
			# time.sleep(3)
		# except: pass
		# from resources.lib.api import premiumize
		# premiumize.library_service()
	# except:pass
	# SELECTIVE UPDATE
	try:
		from resources.lib.api import premiumize
		control.infoDialog('Library Service Started... Please Wait')
		if control.setting('library.deleteold') == 'true': deleteold = True
		else: deleteold = False
		premiumize.selective_update(deleteold=deleteold)
		control.infoDialog('Cloud Sync Process Complete')
		control.execute('UpdateLibrary(video)')	
	except:pass
	
def backupAddon():
	
	profilePath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
	USERDATA     =  str(profilePath)
	if os.path.exists(USERDATA):
		backupdir = control.setting('remote_path')
		if not backupdir == '':
			to_backup = xbmc.translatePath('special://home/userdata/addon_data/')	
			backup_zip = xbmc.translatePath(os.path.join(backupdir,'realizer_settings.zip'))
			from lib_commons import CreateZip
			exclude_database = ['.txt']
			CreateZip(USERDATA, backup_zip, 'Creating Backup', 'Backing up files', '', exclude_database)						
			dialog.ok('Backup Addon','Backup complete','','')
		else:
		   dialog.ok('Backup Addon','No backup location found: Please setup your Backup location in the addon settings','','')
		   xbmc.executebuiltin('RunPlugin(%s?action=openSettings&query=7.0)' % sys.argv[0])
		
def restoreAddon():
	profilePath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
	USERDATA     =  str(profilePath)
	xmlSettings = xbmc.translatePath(os.path.join(profilePath, 'settings.xml'))
	yesDialog = dialog.yesno('Restore From Zip File', 'This will overwrite all your current settings of the addon... Are you sure?', yeslabel='Yes', nolabel='No')
	if yesDialog:
		if os.path.exists(USERDATA):
			zipdir=control.setting('remote_restore_path')
			if zipdir != '' and zipdir != None:
			
				try: shutil.rmtree(profilePath)
				except:pass
				try:
					for root, dirs, files in os.walk(profilePath,topdown=True):
						dirs[:] = [d for d in dirs]
						for name in files:
							try:
								os.remove(os.path.join(root,name))
								os.rmdir(os.path.join(root,name))
							except: pass
								
						for name in dirs:
							try: os.rmdir(os.path.join(root,name)); os.rmdir(root)
							except: pass
				except: pass
			
			
				try: os.remove(xmlSettings)
				except:pass		
				
				if not os.path.exists(profilePath): os.makedirs(profilePath)
				dp = xbmcgui.DialogProgress()
				dp.create("Restoring File","In Progress...",'', 'Please Wait')
				dp.update(0,"", "Extracting Zip Please Wait")
				from lib_commons import ExtractZip
				ExtractZip(zipdir,USERDATA,dp)
				dialog.ok('Restore Settings','Restore Complete','','')
			else:
				dialog.ok('Restore Settings','No item found: Please select your zipfile location in the addon settings','','')
				xbmc.executebuiltin('RunPlugin(%s?action=openSettings&query=7.0)' % sys.argv[0])
	
		
		

		
		
  