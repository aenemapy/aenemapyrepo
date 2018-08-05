"""
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
"""
import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,sys
import urllib2,urllib
import re
import time
import zipfile
from resources.lib.modules import control, maintenance
from datetime import datetime

dp           = xbmcgui.DialogProgress()
dialog 		 = xbmcgui.Dialog()
addonInfo    = xbmcaddon.Addon().getAddonInfo

AddonTitle="EZ Maintenance+"
AddonID ='script.ezmaintenanceplus'


def get_Kodi_Version():
	try: KODIV        =  float(xbmc.getInfoLabel("System.BuildVersion")[:4])
	except: KODIV = 0
	return KODIV

def open_Settings():
	open_Settings = xbmcaddon.Addon(id=AddonID).openSettings()
	
def _get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return unicode( keyboard.getText(), "utf-8" )
    return default
	
def ENABLE_ADDONS():
	for root, dirs, files in os.walk(HOME_ADDONS,topdown=True):
		dirs[:] = [d for d in dirs]
		for addon_name in dirs:
				if not any(value in addon_name for value in EXCLUDES_ADDONS):
					# addLink(addon_name,'url',100,ART+'tool.png',FANART,'')
					try:
						query = '{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":true}, "id":1}' % (addon_name)
						xbmc.executeJSONRPC(query)			
						
					except:
						pass

	
def FIX_SPECIAL():

    HOME =  xbmc.translatePath('special://home')
    dp.create(AddonTitle,"Renaming paths...",'', '')
    url = xbmc.translatePath('special://userdata')
    for root, dirs, files in os.walk(url):
        for file in files:
            if file.endswith(".xml"):
                 dp.update(0,"Fixing","[COLOR dodgerblue]" + file + "[/COLOR]", "Please wait.....")
                 a=open((os.path.join(root, file))).read()
                 b=a.replace(HOME, 'special://home/')
                 f= open((os.path.join(root, file)), mode='w')
                 f.write(str(b))
                 f.close()


def skinswap():

	skin         =  xbmc.getSkinDir()
	KODIV        =  get_Kodi_Version()
	skinswapped = 0
	from resources.lib.modules import skinSwitch

	#SWITCH THE SKIN IF THE CURRENT SKIN IS NOT CONFLUENCE
	if skin not in ['skin.confluence','skin.estuary']:
		choice = xbmcgui.Dialog().yesno(AddonTitle, 'We can try to reset to the default Kodi Skin...','Do you want to Proceed?','', yeslabel='Yes',nolabel='No')
		if choice == 1:

			skin = 'skin.estuary' if KODIV >= 17 else 'skin.confluence'
			skinSwitch.swapSkins(skin)
			skinswapped = 1
			time.sleep(1)
	
	#IF A SKIN SWAP HAS HAPPENED CHECK IF AN OK DIALOG (CONFLUENCE INFO SCREEN) IS PRESENT, PRESS OK IF IT IS PRESENT
	if skinswapped == 1:
		if not xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
			xbmc.executebuiltin( "Action(Select)" )
	
	#IF THERE IS NOT A YES NO DIALOG (THE SCREEN ASKING YOU TO SWITCH TO CONFLUENCE) THEN SLEEP UNTIL IT APPEARS
	if skinswapped == 1:
		while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
			time.sleep(1)
	
	#WHILE THE YES NO DIALOG IS PRESENT PRESS LEFT AND THEN SELECT TO CONFIRM THE SWITCH TO CONFLUENCE.
	if skinswapped == 1:
		while xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
			xbmc.executebuiltin( "Action(Left)" )
			xbmc.executebuiltin( "Action(Select)" )
			time.sleep(1)
	
	skin         =  xbmc.getSkinDir()

	#CHECK IF THE SKIN IS NOT CONFLUENCE
	if skin not in ['skin.confluence','skin.estuary']:
		choice = xbmcgui.Dialog().yesno(AddonTitle, '[COLOR lightskyblue][B]ERROR: AUTOSWITCH WAS NOT SUCCESFULL[/B][/COLOR]','[COLOR lightskyblue][B]CLICK YES TO MANUALLY SWITCH TO CONFLUENCE NOW[/B][/COLOR]','[COLOR lightskyblue][B]YOU CAN PRESS NO AND ATTEMPT THE AUTO SWITCH AGAIN IF YOU WISH[/B][/COLOR]', yeslabel='[B][COLOR green]YES[/COLOR][/B]',nolabel='[B][COLOR lightskyblue]NO[/COLOR][/B]')
		if choice == 1:
			xbmc.executebuiltin("ActivateWindow(appearancesettings)")
			return
		else:
			sys.exit(1)
			
			
# BACKUP ZIP			
def backup(mode='full'):
	KODIV = get_Kodi_Version()

	backupdir = control.setting('download.path')
	if backupdir == '' or backupdir == None: 
		control.infoDialog('Please Setup a Path for Downlads first')
		control.openSettings(query='1.3')
		return
		
	if mode == 'full': 
		defaultName    =  "kodi_backup"
		BACKUPDATA     =  control.HOME
		FIX_SPECIAL()
	elif mode == 'userdata': 
		defaultName    =  "kodi_settings"
		BACKUPDATA     =  control.USERDATA
	else: return
	if os.path.exists(BACKUPDATA):
		if not backupdir == '':
			name = _get_keyboard(default=defaultName, heading='Name your Backup')
			today = datetime.now().strftime('%Y%m%d%H%M')
			today = re.sub('[^0-9]', '', str(today))
			zipDATE = "_%s.zip" % today
			name = re.sub(' ','_', name) + zipDATE
			backup_zip = xbmc.translatePath(os.path.join(backupdir, name))
			exclude_database = ['.pyo','.log']
			
			try:
				maintenance.clearCache(mode='silent')
				maintenance.deleteThumbnails(mode='silent')
				maintenance.purgePackages(mode='silent')
			except:pass
			
			exclude_dirs = ['']
			CreateZip(BACKUPDATA, backup_zip, 'Creating Backup', 'Backing up files', exclude_dirs, exclude_database)						
			dialog.ok(AddonTitle,'Backup complete','','')
		else:
		   dialog.ok(AddonTitle,'No backup location found: Please setup your Backup location','','')

def restoreFolder():
	names = []
	links = []
	zipFolder = control.setting('restore.path')
	if zipFolder == '' or zipFolder == None: 
		control.infoDialog('Please Setup a Zip Files Location first')
		control.openSettings(query='2.0')
		return
	for zipFile in os.listdir(zipFolder):
			if zipFile.endswith(".zip"):
				url = xbmc.translatePath(os.path.join(zipFolder, zipFile))
				names.append(zipFile)
				links.append(url)
	select = control.selectDialog(names)
	if select != -1: restore(links[select])

def restore(zipFile):
	yesDialog = dialog.yesno(AddonTitle, 'This will overwrite all your current settings ... Are you sure?', yeslabel='Yes', nolabel='No')
	if yesDialog:
		try:
			dp = xbmcgui.DialogProgress()
			dp.create("Restoring File","In Progress...",'', 'Please Wait')
			dp.update(0, "", "Extracting Zip Please Wait")
			ExtractZip(zipFile, control.HOME, dp)
			dialog.ok(AddonTitle,'Restore Complete','','')
			xbmc.executebuiltin('ShutDown')
		except:pass
		
		

def CreateZip(folder, zip_filename, message_header, message1, exclude_dirs, exclude_files):
    abs_src = os.path.abspath(folder)
    for_progress = []
    ITEM =[]
    dp = xbmcgui.DialogProgress()
    dp.create(message_header, message1)
    try: os.remove(zip_filename)
    except: pass		
    for base, dirs, files in os.walk(folder):
        for file in files: ITEM.append(file)
    N_ITEM =len(ITEM)
    count = 0

    zip_file = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, allowZip64 = True)
    for dirpath, dirnames, filenames in os.walk(folder):
		try:
			dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
			filenames[:] = [f for f in filenames if f not in exclude_files]		

			for file in filenames:
				count += 1
				for_progress.append(file)
				progress = len(for_progress) / float(N_ITEM) * 100  
				dp.update(int(progress),"Backing Up", 'FILES: ' + str(count) + '/' + str(N_ITEM)  + '   [COLOR lime]' + str(file) + '[/COLOR]', 'Please Wait')
				file = os.path.join(dirpath, file)
				file = os.path.normpath(file)
				arcname = file[len(abs_src) + 1:]
				zip_file.write(file, arcname)
		except:pass
    zip_file.close()


	
# EXTRACT ZIP	
def ExtractZip(_in, _out, dp=None):
    if dp: return ExtractWithProgress(_in, _out, dp)
    return ExtractNOProgress(_in, _out)
        
def ExtractNOProgress(_in, _out):
    try:
        zin = zipfile.ZipFile(_in, 'r')
        zin.extractall(_out)
    except Exception, e:
        print str(e)
    return True

def ExtractWithProgress(_in, _out, dp):
    zin = zipfile.ZipFile(_in,  'r')
    nFiles = float(len(zin.infolist()))
    count  = 0
    errors = 0
    try:
        for item in zin.infolist():
            count += 1
            update = count / nFiles * 100
            try: name = os.path.basename(item.filename)
            except: name = item.filename
            label = '[COLOR skyblue][B]%s[/B][/COLOR]' % str(name)
            dp.update(int(update),'Extracting... Errors:  ' + str(errors) , label, '')
            try: zin.extract(item, _out)
            except Exception, e:
				print ("EXTRACTING ERRORS", e)
				pass

    except Exception, e:
        print str(e)
    return True

# INSTALL BUILD
def buildInstaller(url):
	destination = dialog.browse(type=0, heading='Select Download Directory', shares='files',useThumbs=True, treatAsFolder=True, enableMultiple=False)
	if destination: 
		dest = xbmc.translatePath(os.path.join(destination, 'custom_build.zip'))
		downloader(url, dest)
		time.sleep(2)
		dp.create("Installing Build","In Progress...",'', 'Please Wait')
		dp.update(0, "", "Extracting Zip Please Wait")
		ExtractZip(dest, control.HOME, dp)
		time.sleep(2)	
		dp.close()
		dialog.ok(AddonTitle,'Installation Complete...','Your interface will now be reset','Click ok to Start...')
		xbmc.executebuiltin('LoadProfile(Master user)')	
# DOWNLOADER
class customdownload(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
	
def downloader(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create(AddonTitle,"",' ', ' ')
    dp.update(0)
    start_time=time.time()
    customdownload().retrieve(url, dest, lambda nb, bs, fs, url=url: _pbhook(nb, bs, fs, dp, start_time))
     
def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100)
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
            e = 'Speed: %.02f Kb/s ' % kbps_speed 
            e += 'ETA: %02d:%02d' % divmod(eta, 60)
            string = 'Downloading... Please Wait...'
            dp.update(percent, mbs, e,string)
        except: 
            percent = 100 
            dp.update(percent)
            dp.close()
            return
			
        if dp.iscanceled(): 
			raise Exception("Canceled")
			dp.close()
			
##############################    END    #########################################