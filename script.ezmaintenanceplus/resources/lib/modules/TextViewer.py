import os
import string
import xbmc
import xbmcaddon
import xbmcgui

Addon = xbmcaddon.Addon()
addon = Addon.getAddonInfo('id')
addonName = Addon.getAddonInfo('name')
moduleName = 'Log Viewer'
dialog = xbmcgui.Dialog()
contents = ''
path = ''

# get actioncodes from keymap.xml
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT_ITEM = 7


class Viewer(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath):
        self.previous_menu = 10
        self.back = 92
        self.page_up = 5
        self.page_down = 6
        
        # XML id's
        self.main_window = 1100
        self.title_box_control = 20301
        self.content_box_control = 20302
        self.list_box_control = 20303
        self.line_number_box_control = 20201
        self.scroll_bar = 20212
    
    def onInit(self):
        # title box
        title_box = self.getControl(self.title_box_control)
        title_box.setText(str.format('%s %s') % (addonName, moduleName))
        
        # content box
        content_box = self.getControl(self.content_box_control)
        content_box.setText(contents)
        
        # Set initial focus
        self.setFocusId(self.scroll_bar)

    def onAction(self, action):
        # non Display Button control
        if action == self.previous_menu:
            self.close()
        elif action == self.back:
            self.close()
    
    def onClick(self, control_id):
        if control_id == 20293:
            self.close()
            text_view(path)
    
    def onFocus(self, control_id):
        pass


def text_view(loc='', data=''):
    global contents
    global path
    contents = ''
    path = loc
    # todo, path can be a url to an internet file
    if not path and not data: return
    if path and not data:
        if 'http' in string.lower(path):
            # todo, open internet files from a url path
            dialog.ok('Notice', 'This feature is not yet available')
            return
        # Open and read the file from path location
        temp_file = open(path, 'rb')
        contents = temp_file.read()
        temp_file.close()
    # Send contents to text display function
    elif data:
        contents = data
    if not contents:
        dialog.ok('Notice', 'The file was empty')
        return
    contents = contents.replace(' ERROR: ', ' [COLOR red]ERROR[/COLOR]: ') \
        .replace(' WARNING: ', ' [COLOR gold]WARNING[/COLOR]: ')
    
    win = Viewer('textview-skin.xml', Addon.getAddonInfo('path'))
    win.doModal()
    del win

# To call module put the following in the addon list or context menu
# import TextViewer
# TextViewer.text_view('log')