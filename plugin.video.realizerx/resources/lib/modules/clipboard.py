# -*- coding: utf-8 -*-

from . import pyperclip

# Required for Ubuntu:
# sudo apt install xsel
    
class Clipboard(object):

    @classmethod
    def __message(self, id, value, type = None):
        message = ''

        return message

    @classmethod
    def copy(self, value, notify = False, type = None):
        if not value:
            return False

        try:
            pyperclip.copy(value)
            id = 33033
        except:
            id = None

        if notify == True:
            #print("NOTIFY")
        return True

    @classmethod
    def paste(self, notify = False, type = None):
        try:
            value = pyperclip.paste()
            if notify == True:
                #print("NOTIFY")
            return value
        except:
            return None
