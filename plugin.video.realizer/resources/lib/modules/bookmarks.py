# -*- coding: utf-8 -*-
'''
    realizer Add-on
    Copyright (C) 2016 realizer

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


import re,sys,json,time,xbmc
import hashlib,urllib,os,zlib,base64,codecs,xmlrpclib


try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

from resources.lib.modules import control
from resources.lib.modules import cleantitle

class bookmarks:
    def getPlayer(self, name):
        try:
            offset = '0'

            if not control.setting('bookmarks') == 'true': raise Exception()
            idFile = cleantitle.get(name)

            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
            match = dbcur.fetchone()
            self.offset = str(match[1])
            dbcon.commit()

            if self.offset == '0': raise Exception()
			
			# AUTO RESUME
            if control.setting('bookmarks.autoresume') == 'true': return self.offset

            minutes, seconds = divmod(float(self.offset), 60) ; hours, minutes = divmod(minutes, 60)
            label = '%02d:%02d:%02d' % (hours, minutes, seconds)
            label = (control.lang(32502) % label).encode('utf-8')

            try: yes = control.dialog.contextmenu([label, control.lang(32501).encode('utf-8'), ])
            except: yes = control.yesnoDialog(label, '', '', str(name), control.lang(32503).encode('utf-8'), control.lang(32501).encode('utf-8'))

            if yes: self.offset = '0'

            return self.offset
        except:
            return offset
			
			
    def get(self, name):
        try:
            offset = '0'

            if not control.setting('bookmarks') == 'true': raise Exception()
            idFile = cleantitle.get(name)

            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
            match = dbcur.fetchone()
            self.offset = str(match[1])
            dbcon.commit()

            if self.offset == '0' or self.offset == None: raise Exception()

            return self.offset
        except:
            return offset

    def reset(self, currentTime, totalTime, name):
        try:
            if not control.setting('bookmarks') == 'true': raise Exception()

            timeInSeconds = str(currentTime)
            ok = int(currentTime) > 180 and (currentTime / totalTime) <= .92

            idFile = cleantitle.get(name)

            control.makeFile(control.dataPath)
            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
            dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
            if ok: dbcur.execute("INSERT INTO bookmark Values (?, ?)", (idFile, timeInSeconds))
            dbcon.commit()
        except:
            pass

    def delete(self, name):
        try:
            
            if not control.setting('bookmarks') == 'true': raise Exception()
            idFile = cleantitle.get(name)

            control.makeFile(control.dataPath)
            dbcon = database.connect(control.bookmarksFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
            dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
            dbcon.commit()
        except:
            pass

