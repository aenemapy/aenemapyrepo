import os
import glob
import time
import xml.etree.ElementTree as ET
try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
import xbmc
import xbmcaddon
import xbmcvfs
import datetime
from resources.lib.api import premiumize
from resources.lib.modules import control
xml_file = xbmcvfs.translatePath(os.path.join('special://home/userdata','sources.xml'))
timeNow = datetime.datetime.now().strftime('%Y%m%d')

def checkinfo():

    validAccount = premiumize.validAccount()

    firstSetup = control.setting('first.setup')
    popup      = control.setting('popup.date')


    if not validAccount:
        from resources.lib.modules import deviceAuthDialog
        authDialog = deviceAuthDialog.DonationDialog('firstrun.xml', xbmcaddon.Addon().getAddonInfo('path'), code='', url='')
        authDialog.doModal()
        del authDialog
        control.openSettings('0.0')

    elif (popup == '0' or ((int(timeNow) - int(popup)) > 30)):
        from resources.lib.modules import deviceAuthDialog
        authDialog = deviceAuthDialog.DonationDialog('donations.xml', xbmcaddon.Addon().getAddonInfo('path'), code='', url='')
        authDialog.doModal()
        del authDialog
        control.setSetting(id='popup.date', value=timeNow)


#control.setSetting(id='first.start', value='true') # FORCE NEW CACHE
#firstSetup = control.setting('first.setup')

#if firstSetup != 'true':
#	from resources.lib.modules import setuptools
#	newvalue = '1'

#	setuptools.FirstStart()
#	control.setSetting(id='first.setup', value='true') # SETUP LIBRARY PATH IN BROWSER


def FirstStart():
    library_movies = control.setting('meta.library.movies')
    library_tv = control.setting('meta.library.tv')
    check_xml()

    if not xbmcvfs.exists(library_movies): control.makeFile(library_movies)
    if not xbmcvfs.exists(library_tv): control.makeFile(library_tv)
    try:
            LANG = 'en'
            source_thumbnail = xbmcvfs.translatePath(os.path.join('special://home/addons/plugin.video.realizerx','icon.png'))
            source_name = "realizer TV SHOWS"
            source_content = "('%s','tvshows','metadata.tvdb.com','',0,0,'<settings version=\"2\"><setting id=\"absolutenumber\" default=\"true\">false</setting><setting id=\"alsoimdb\">true</setting><setting id=\"dvdorder\" default=\"true\">false</setting><setting id=\"fallback\">true</setting><setting id=\"fallbacklanguage\">es</setting><setting id=\"fanart\">true</setting><setting id=\"language\" default=\"true\">en</setting><setting id=\"RatingS\" default=\"true\">TheTVDB</setting><setting id=\"usefallbacklanguage1\">true</setting></settings>',0,0,NULL,NULL)" % library_tv

            _add_source_xml(xml_file, source_name, library_tv, source_thumbnail)
            _set_source_content(source_content)
    except: pass
    try:
            LANG = 'en'
            source_content = "('%s','movies','metadata.themoviedb.org','',2147483647,1,'<settings version=\"2\"><setting id=\"certprefix\" default=\"true\">Rated </setting><setting id=\"fanart\">true</setting><setting id=\"imdbanyway\">true</setting><setting id=\"keeporiginaltitle\" default=\"true\">false</setting><setting id=\"language\" default=\"true\">en</setting><setting id=\"RatingS\" default=\"true\">TMDb</setting><setting id=\"tmdbcertcountry\" default=\"true\">us</setting><setting id=\"trailer\">true</setting></settings>',0,0,NULL,NULL)" % library_movies

            source_thumbnail = xbmcvfs.translatePath(os.path.join('special://home/addons/plugin.video.realizerx','icon.png'))
            source_name = "realizer MOVIES"
            _add_source_xml(xml_file, source_name, library_movies, source_thumbnail)
            _set_source_content(source_content)
    except: pass

    control.infoDialog('Library Paths Added')

def scan_library(type="video"):
    while not xbmc.abortRequested and \
     (xbmc.getCondVisibility('Library.IsScanning') or \
     xbmc.getCondVisibility('Window.IsActive(progressdialog)')):
        xbmc.sleep(1000)
    xbmc.executebuiltin('UpdateLibrary(video)')
    xbmc.executebuiltin('UpdateLibrary(music)')

def check_xml():
    if not os.path.exists(xml_file):
        with open(xml_file, "w") as f:
            f.write("""<sources>
    <programs>
        <default pathversion="1" />
    </programs>
    <video>
        <default pathversion="1" />
    </video>
    <music>
        <default pathversion="1" />
    </music>
    <pictures>
        <default pathversion="1" />
    </pictures>
    <files>
        <default pathversion="1" />
    </files>
</sources>""")


def _add_source_xml(xml_file, name, path, thumbnail):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sources = root.find('video')
    existing_source = None
    for source in sources.findall('source'):
        xml_name = source.find("name").text
        xml_path = source.find("path").text
        try: xml_thumbnail = source.find("thumbnail").text
        except: xml_thumbnail = ""
        if xml_name == name or xml_path == path:
            existing_source = source
            break
    if existing_source is not None:
        xml_name = source.find("name").text
        xml_path = source.find("path").text
        try: xml_thumbnail = source.find("thumbnail").text
        except: xml_thumbnail = ""
        if xml_name == name and xml_path == path and xml_thumbnail == thumbnail:
            return False
        elif xml_name == name:
            source.find("path").text = path
            source.find("thumbnail").text = thumbnail
        elif xml_path == path:
            source.find("name").text = name
            source.find("thumbnail").text = thumbnail
        else:
            source.find("path").text = path
            source.find("name").text = name
    else:
        new_source = ET.SubElement(sources, 'source')
        new_name = ET.SubElement(new_source, 'name')
        new_name.text = name
        new_path = ET.SubElement(new_source, 'path')
        new_thumbnail = ET.SubElement(new_source, 'thumbnail')
        new_allowsharing = ET.SubElement(new_source, 'allowsharing')
        new_path.attrib['pathversion'] = "1"
        new_thumbnail.attrib['pathversion'] = "1"
        new_path.text = path
        new_thumbnail.text = thumbnail
        new_allowsharing.text = "true"
    _indent_xml(root)
    tree.write(xml_file)
    return True

def _indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def _get_source_attr(xml_file, name, attr):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sources = root.find('video')
    for source in sources.findall('source'):
        xml_name = source.find("name").text
        if xml_name == name:
            return source.find(attr).text
    return None

#########   Database functions  #########

def _db_execute(db_name, command):
    databaseFile = _get_database(db_name)
    if not databaseFile:
        return False
    dbcon = database.connect(databaseFile)
    dbcur = dbcon.cursor()
    dbcur.execute(command)
    #try:
    #    dbcur.execute(command)
    #except database.Error as e:
    #    #print "MySQL Error :", e.args[0], q.decode("utf-8")
    #    return False
    dbcon.commit()
    return True

def _get_database(db_name):
    path_db = "special://profile/Database/" + db_name
    filelist = glob.glob(xbmcvfs.translatePath(path_db))
    if filelist:
        return filelist[-1]
    return None

def _remove_source_content(path):
    q = "DELETE FROM path WHERE strPath LIKE '%{0}%'".format(path)
    return _db_execute("MyVideos*.db", q)

def _set_source_content(content):
    q = "INSERT OR REPLACE INTO path (strPath,strContent,strScraper,strHash,scanRecursive,useFolderNames,strSettings,noUpdate,exclude,dateAdded,idParentPath) VALUES "
    q += content
    return _db_execute("MyVideos*.db", q)
