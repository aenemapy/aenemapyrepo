import xbmc, time
import xbmcgui, xbmcaddon
from platform import machine
from resources.lib.modules import control
ACTION_PLAYER_STOP = 13
OS_MACHINE = machine()

def nextup(episode):
    if episode == None or episode == '':
        episode = {}
        episode['poster'] = control.addonIcon()
        episode['fanart'] = control.addonIcon()
        episode['plot']   = ''
        episode['title']  = 'No episode data found'
        episode['tvshowtitle'] = 'No show data found'
        episode['season'] = '0'
        episode['episode'] = '0'
        episode['plot'] = ''
        episode['rating'] = '0.0'
        episode['year'] = '0'
        #print ("NEXTUP >>> NO EPISODE DATA FOUND")
        return False
        
    nextup_action = control.setting('nextup.action')
    skin_native = control.setting('nextup.skin.native')
    try:
        if skin_native == 'true': nextUpPage = NextUpInfo("script-nextup-notification-NextUpInfo.xml", control.addonPath, "default", "1080i")
        else: nextUpPage = NextUpInfo("script-nextup.xml", control.addonPath, "default", "1080i")
        nextUpPage.setItem(episode) 
        nextUpPage.show()
        
        playTime = xbmc.Player().getTime()
        totalTime =  xbmc.Player().getTotalTime()
                        
        while xbmc.Player().isPlaying()and (totalTime - playTime > 5) and not nextUpPage.isCancel() and not nextUpPage.isWatchNow():
            xbmc.sleep(100)
            try:
                playTime = xbmc.Player().getTime()
                totalTime = xbmc.Player().getTotalTime()
            except:
                pass    
        
        if nextUpPage.isWatchNow(): 
            try: nexUpPage.closeDialog()
            except:pass     
            xbmc.Player().stop()
            return True
            
        elif nextUpPage.isCancel():
            try: nexUpPage.closeDialog()
            except:pass             
            return False

        elif nextup_action == '0': # DEFAULT PLAY
            try: nexUpPage.closeDialog()
            except:pass     
            return True         

        else: 
            try: nexUpPage.closeDialog()
            except:pass             
            return False
            
            
    except: return False
        

        
        
class NextUpInfo(xbmcgui.WindowXMLDialog):
    item = None
    cancel = False
    watchnow = False

    def __init__(self, *args, **kwargs):
        if OS_MACHINE[0:5] == 'armv7':
            xbmcgui.WindowXMLDialog.__init__(self)
        else:
            xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        self.action_exitkeys_id = [10, 13]

        try: image = self.item['poster']
        except: image = '0'
        if "fanart" in self.item: fanartimage = self.item['fanart']
        else: fanartimage = '0'
        if "fanart" in self.item: landscapeimage = self.item['fanart']
        else: landscapeimage = control.addonIcon()
        if "thumb" in self.item: thumb = self.item['thumb']
        else: thumb = '0'       
        if thumb != '0' and thumb != None: image = fanartimage = landscapeimage = thumb
        elif fanartimage != '0' and fanartimage != None: image = thumb = landscapeimage = fanartimage
        elif image != '0' and image != None: fanartimage = thumb = landscapeimage = image
                
        overview = self.item['plot']
        tvshowtitle = self.item['tvshowtitle']
        name = self.item['title']
        playcount = ''

        season = self.item['season']
        episodeNum = self.item['episode']
        episodeInfo = str(season) + 'x' + str(episodeNum) + '.'

        rating = str(round(float(self.item['rating']),1))
        year = self.item['year']
        info = year

        # set the dialog data
        self.getControl(3000).setLabel(name)
        self.getControl(3001).setText(overview)
        self.getControl(3002).setLabel(episodeInfo)
        self.getControl(3004).setLabel(info)
        self.getControl(7777).setLabel(thumb)

        if rating is not None:
            self.getControl(3003).setLabel(rating)
        else:
            self.getControl(3003).setVisible(False)

        try:
            tvShowControl = self.getControl(3007)
            if tvShowControl != None:
                tvShowControl.setLabel(tvshowtitle)
        except:
            pass

        try:
            posterControl = self.getControl(3009)
            if posterControl != None:
                posterControl.setImage(image)
        except:
            pass

        try:
            fanartControl = self.getControl(3005)
            if fanartControl != None:
                fanartControl.setImage(fanartimage)
        except:
            pass

        try:
            thumbControl = self.getControl(3008)
            if thumbControl != None:
                self.getControl(3008).setImage(thumb)
        except:
            pass

        try:
            landscapeControl = self.getControl(3010)
            if landscapeControl != None:
                self.getControl(3010).setImage(landscapeimage)
        except:
            pass

        try:
            clearartimageControl = self.getControl(3006)
            if clearartimageControl != None:
                self.getControl(3006).setImage(clearartimage)
        except:
            pass

        try:
            seasonControl = self.getControl(3015)
            if seasonControl != None:
                seasonControl.setLabel(str(season))
        except:
            pass

        try:
            episodeControl = self.getControl(3016)
            if episodeControl != None:
                episodeControl.setLabel(str(episodeNum))
        except:
            pass

        try:
            resolutionControl = self.getControl(3011)
            if resolutionControl != None:
                resolution1 = self.item['streamdetails'].get('video')
                resolution = resolution1[0].get('height')
                resolutionControl.setLabel(str(resolution))
        except:
            pass

        try:
            playcountControl = self.getControl(3018)
            if playcountControl != None:
                playcountControl.setLabel(str(playcount))
        except:
            pass

    def setItem(self, item):
        self.item = item

    def setCancel(self, cancel):
        self.cancel = cancel

    def isCancel(self):
        return self.cancel

    def setWatchNow(self, watchnow):
        self.watchnow = watchnow

    def isWatchNow(self):
        return self.watchnow

    def onFocus(self, controlId):
        pass

    def doAction(self):
        pass

    def closeDialog(self):
        self.close()

    def onClick(self, controlID):

        xbmc.log('nextup info onclick: ' + str(controlID))

        if controlID == 3012:

            # watch now
            self.setWatchNow(True)
            self.close()
        elif controlID == 3013:

            # cancel
            self.setCancel(True)
            self.close()

        pass

    def onAction(self, action):

        xbmc.log('nextup info action: ' + str(action.getId()))
        if action == ACTION_PLAYER_STOP:
            self.close()
