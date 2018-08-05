import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import time
from resources.lib.modules import maintenance

AddonID ='script.ezmaintenanceplus'
packagesdir    =  xbmc.translatePath(os.path.join('special://home/addons/packages',''))
thumbnails    =  xbmc.translatePath('special://home/userdata/Thumbnails')
dialog = xbmcgui.Dialog()
setting = xbmcaddon.Addon().getSetting
iconpath = xbmc.translatePath(os.path.join('special://home/addons/' + AddonID,'icon.png'))
# if setting('autoclean') == 'true':
	# control.clearCache()
	
notify_mode = setting('notify_mode')
auto_clean  = setting('startup.cache')
filesize = int(setting('filesize_alert'))
filesize_thumb = int(setting('filesizethumb_alert'))
maxpackage_zips = int(setting('packagenumbers_alert'))

total_size2 = 0
total_size = 0
count = 0

for dirpath, dirnames, filenames in os.walk(packagesdir):
	count = 0
	for f in filenames:
		count += 1
		fp = os.path.join(dirpath, f)
		total_size += os.path.getsize(fp)
total_sizetext = "%.0f" % (total_size/1024000.0)
	
if int(total_sizetext) > filesize:
	choice2 = xbmcgui.Dialog().yesno("[COLOR=red]Autocleaner[/COLOR]", 'The packages folder is [COLOR red]' + str(total_sizetext) +' MB [/COLOR] - [COLOR red]' + str(count) + '[/COLOR] zip files', 'The folder can be cleaned up without issues to save space...', 'Do you want to clean it now?', yeslabel='Yes',nolabel='No')
	if choice2 == 1:
		maintenance.purgePackages()
			
for dirpath2, dirnames2, filenames2 in os.walk(thumbnails):
	for f2 in filenames2:
		fp2 = os.path.join(dirpath2, f2)
		total_size2 += os.path.getsize(fp2)
total_sizetext2 = "%.0f" % (total_size2/1024000.0)

if int(total_sizetext2) > filesize_thumb:
	choice2 = xbmcgui.Dialog().yesno("[COLOR=red]Autocleaner[/COLOR]", 'The images folder is [COLOR red]' + str(total_sizetext2) + ' MB   [/COLOR]', 'The folder can be cleaned up without issues to save space...', 'Do you want to clean it now?', yeslabel='Yes',nolabel='No')
	if choice2 == 1:
		maintenance.deleteThumbnails()
		
total_sizetext = "%.0f" % (total_size/1024000.0)
total_sizetext2 = "%.0f" % (total_size2/1024000.0)
	
if notify_mode == 'true': xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % ('Maintenance Status',  'Packages: '+ str(total_sizetext) +  ' MB'  ' - Images: ' + str(total_sizetext2) + ' MB' , '5000', iconpath))
time.sleep(3)
if auto_clean  == 'true': maintenance.clearCache()





