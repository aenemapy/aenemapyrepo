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
from resources.lib.modules import control
from datetime import datetime

dp           = xbmcgui.DialogProgress()
dialog 		 = xbmcgui.Dialog()
addonInfo    = xbmcaddon.Addon().getAddonInfo

AddonTitle="EZ Maintenance+"
AddonID ='script.ezmaintenanceplus'


def xml_data_advSettings_old(size):
	xml_data="""<advancedsettings>
	  <network>
	    <curlclienttimeout>10</curlclienttimeout>
	    <curllowspeedtime>20</curllowspeedtime>
	    <curlretries>2</curlretries>    
		<cachemembuffersize>%s</cachemembuffersize> 
		<buffermode>2</buffermode>
		<readbufferfactor>20</readbufferfactor>
	  </network>
</advancedsettings>""" % size
	return xml_data
	
def xml_data_advSettings_New(size):
	xml_data="""<advancedsettings>
	  <network>
	    <curlclienttimeout>10</curlclienttimeout>
	    <curllowspeedtime>20</curllowspeedtime>
	    <curlretries>2</curlretries>    
	  </network>
	  <cache>
		<memorysize>%s</memorysize> 
		<buffermode>2</buffermode>
		<readfactor>20</readfactor>
	  </cache>
</advancedsettings>""" % size
	return xml_data







def write_ADV_SETTINGS_XML(file):    
    if not os.path.exists(xml_file):
        with open(xml_file, "w") as f:
            f.write(xml_data)


def advancedSettings():
	XML_FILE   =  xbmc.translatePath(os.path.join('special://home/userdata' , 'advancedsettings.xml'))
	MEM        =  xbmc.getInfoLabel("System.Memory(total)")
	FREEMEM    =  xbmc.getInfoLabel("System.FreeMemory")
	BUFFER_F   =  re.sub('[^0-9]','',FREEMEM)
	BUFFER_F   = int(BUFFER_F) / 3
	BUFFERSIZE = BUFFER_F * 1024 * 1024
	try: KODIV        =  float(xbmc.getInfoLabel("System.BuildVersion")[:4])
	except: KODIV = 16

		
	choice = dialog.yesno(AddonTitle, 'FREE MEMORY: ' + str(FREEMEM) ,'Based on your free Memory your optimal buffersize is: ' + str(BUFFER_F) + ' MB','Choose an Option below...', yeslabel='Use Optimal',nolabel='Input a Value')
	if choice == 1: 
		with open(XML_FILE, "w") as f:
			if KODIV >= 17: xml_data = xml_data_advSettings_New(str(BUFFERSIZE))
			else: xml_data = xml_data_advSettings_old(str(BUFFERSIZE))
			
			f.write(xml_data)
			dialog.ok(AddonTitle,'Buffer Size Set to: ' + str(BUFFERSIZE),'Please restart Kodi for settings to apply.','')
	
	elif choice == 0:
		BUFFERSIZE = _get_keyboard( default=str(BUFFERSIZE), heading="INPUT BUFFER SIZE")
		with open(XML_FILE, "w") as f:
			if KODIV >= 17: xml_data = xml_data_advSettings_New(str(BUFFERSIZE))
			else: xml_data = xml_data_advSettings_old(str(BUFFERSIZE))
			f.write(xml_data)
			dialog.ok(AddonTitle,'Buffer Size Set to: ' + str(BUFFERSIZE),'Please restart Kodi for settings to apply.','')
	

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
	KODIV        =  float(xbmc.getInfoLabel("System.BuildVersion")[:4])
	skinswapped = 0

	#SWITCH THE SKIN IF THE CURRENT SKIN IS NOT CONFLUENCE
	if skin not in ['skin.confluence','skin.estuary']:
		choice = xbmcgui.Dialog().yesno(AddonTitle, 'Please Wait while we try to reset to the default Kodi Skin...','','', yeslabel='Yes',nolabel='No')
		if choice == 0:
			sys.exit(1)
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
	backupdir = dialog.browse(type=0, heading='Select Backup Directory', shares='files',useThumbs=True, treatAsFolder=True, enableMultiple=False)
	if mode == 'full': 
		BACKUPDATA     =  control.HOME
		FIX_SPECIAL()
	elif mode == 'userdata': BACKUPDATA     =  control.USERDATA
	else: return
	if os.path.exists(BACKUPDATA):
		if not backupdir == '':
			name = _get_keyboard(default='kodi_backup', heading='Name your Backup')
			today = datetime.now().strftime('%Y%m%d%H%M')
			today = re.sub('[^0-9]', '', str(today))
			zipDATE = "_%s.zip" % today
			name = re.sub(' ','_', name) + zipDATE
			backup_zip = xbmc.translatePath(os.path.join(backupdir, name))
			exclude_database = ['.pyo','.log']
			exclude_dirs = ['cache','packages','Thumbnails']
			CreateZip(BACKUPDATA, backup_zip, 'Creating Backup', 'Backing up files', exclude_dirs, exclude_database)						
			dialog.ok(AddonTitle,'Backup complete','','')
		else:
		   dialog.ok(AddonTitle,'No backup location found: Please setup your Backup location','','')

def restore():
	yesDialog = dialog.yesno(AddonTitle, 'This will overwrite all your current settings ... Are you sure?', yeslabel='Yes', nolabel='No')
	if yesDialog:
		try:
			zipFile = dialog.browse(type=1, heading='Select Backup File', shares='files',useThumbs=True, treatAsFolder=False, enableMultiple=False)
			dp = xbmcgui.DialogProgress()
			dp.create("Restoring File","In Progress...",'', 'Please Wait')
			dp.update(0, "", "Extracting Zip Please Wait")
			ExtractZip(zipdir, control.HOME, dp)
			dialog.ok(AddonTitle,'Restore Complete','','')
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
        for file in files:
            ITEM.append(file)
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
            filenamefull = item.filename
            dp.update(int(update),'Extracting... Errors:  ' + str(errors) ,filenamefull, '')
            try: zin.extract(item, _out)
            except Exception, e:
				print ("EXTRACTING ERRORS", e)
				pass

    except Exception, e:
        print str(e)
        

    return True


	
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
        if dp.iscanceled(): 
			raise Exception("Canceled")
			dp.close()
			
##############################    END    #########################################