import re
import json
import urllib
import urllib2
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import os
import inspect
from resources.lib.modules import downloadzip
from resources.lib.modules import control

	
	
def downloadAPK(name, url):
    if url == None: return
    dest = control.setting('download.path')
    if dest == '' or dest == None: control.infoDialog('Download Location is Empty...')
	

    image = control.icon

    try: headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
    except: headers = dict('')


    content = re.compile('(.+?)\sS(\d*)E\d*$').findall(name)
    transname = name.translate(None, '\/:*?"<>|')

    dest = control.transPath(dest)
    control.makeFile(dest)
    dest = os.path.join(dest, transname)

    sysheaders = urllib.quote_plus(json.dumps(headers))

    sysurl = urllib.quote_plus(url)

    systitle = urllib.quote_plus(name)

    sysimage = urllib.quote_plus(image)

    sysdest = urllib.quote_plus(dest)

    script = inspect.getfile(inspect.currentframe())

    dp = xbmcgui.DialogProgress()
    dp.create(name,"Please Wait...")		
    try:
		downloadzip.download(url, dest, dp)
		control.infoDialog('Download Completed...')
    except: control.infoDialog('Unable to Download...')
	
	
def installAPK(name, url):
    if url == None: return
    dest = control.setting('download.path')
    if dest == '' or dest == None: control.infoDialog('Download Location is Empty...')
	

    image = control.icon

    try: headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
    except: headers = dict('')


    content = re.compile('(.+?)\sS(\d*)E\d*$').findall(name)
    transname = name.translate(None, '\/:*?"<>|')

    dest = control.transPath(dest)
    control.makeFile(dest)
    dest = os.path.join(dest, transname)

    sysheaders = urllib.quote_plus(json.dumps(headers))

    sysurl = urllib.quote_plus(url)

    systitle = urllib.quote_plus(name)

    sysimage = urllib.quote_plus(image)

    sysdest = urllib.quote_plus(dest)

    script = inspect.getfile(inspect.currentframe())

    dp = xbmcgui.DialogProgress()
    dp.create(name,"Please Wait...")		
    try:
		r = downloadzip.download(url, dest, dp)
		if r == '0': control.infoDialog('Download Interrupted...')
		else: control.infoDialog('Download Completed...')
    except: control.infoDialog('Unable to Download...')
	
	
    apkfile = dest
    xbmc.executebuiltin('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+apkfile+'")')



