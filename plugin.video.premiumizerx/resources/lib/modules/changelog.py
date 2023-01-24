
import xbmc,xbmcgui,xbmcaddon,xbmcvfs,os
from resources.lib.modules import control

def get():
    try:
        #print ("CHANGELOG")

        LastVersion    = control.setting('last.version')
        if LastVersion == '' or LastVersion == None: LastVersion = '0'
        AddonVersion   = xbmcaddon.Addon().getAddonInfo('version')

        if LastVersion != AddonVersion:
            control.setSetting(id='last.version', value=AddonVersion)

            addonInfo = xbmcaddon.Addon().getAddonInfo
            addonPath = xbmcvfs.translatePath(addonInfo('path'))
            changelogfile = os.path.join(addonPath, 'changelog.txt')
            r = open(changelogfile)
            text = r.read()

            label = '%s - %s' % ("What's New", xbmcaddon.Addon().getAddonInfo('name'))

            id = 10147

            xbmc.executebuiltin('ActivateWindow(%d)' % id)
            xbmc.sleep(100)

            win = xbmcgui.Window(id)

            retry = 50
            while (retry > 0):
                try:
                    xbmc.sleep(10)
                    win.getControl(1).setLabel(label)
                    win.getControl(5).setText(text)
                    retry = 0
                except:
                    retry -= 1

            return '1'
    except:
        return '1'


