# -*- coding: utf-8 -*-
'''
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

import re,urllib.request,urllib.parse,urllib.error,urllib.parse,os,xbmcvfs
from resources.lib.modules import control

try:
    from sqlite3 import dbapi2 as db, OperationalError
except ImportError:
    from pysqlite2 import dbapi2 as db, OperationalError

def clearPlaycount():
    DATABASE = control.playcountDB
    try: 
        os.remove(DATABASE)
        return True
    except: return False
    
    
def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
    
def _get_connection_cursor_playcount():
    conn = _get_connection_playcount()
    return conn.cursor()


def _get_connection_cursor_meta():
    conn = _get_connection_meta()
    return conn.cursor()
    
def _get_connection_playcount():
    control.makeFile(control.dataPath)
    conn = db.connect(control.playcountDB)
    conn.row_factory = _dict_factory
    return conn
    
def _get_connection_meta():
    control.makeFile(control.dataPath)
    conn = db.connect(control.metaDB)
    conn.row_factory = _dict_factory
    return conn    
    
def open_database():
    DATABASE = control.metaDB
    connection = database.connect(DATABASE)
    #connection.text_factory = str
    connection.text_factory = lambda x: str(x, 'utf-8', 'ignore')
    connection.row_factory = database.Row
    #print("DB connection opened to {0}.".format(DATABASE))
    return connection

def metaMovies(imdb=None, tmdb=None):
    try:
    
        if imdb != None and imdb != '' and imdb != '0' and imdb != 'None': 
            type = 'imdb'
            id = imdb
        elif tmdb != None and tmdb != '' and tmdb != '0' and tmdb != 'None': 
            type = 'tmdb'
            id = tmdb
        

        cursor = _get_connection_cursor_meta()
        cursor.execute("SELECT * FROM movies WHERE %s = '%s'" % (type, id))
        row = cursor.fetchone()
        meta = {}
        for id in list(row.keys()): meta[id] = row[id]
        return meta
        #print(("[METALIBRARY]", meta))
    except: 
        return

def metaTV(imdb=None, tmdb=None, tvdb=None):
    try:

        if tvdb != None and tvdb != '' and tvdb != '0' and tvdb != 'None': 
            type = 'tvdb'
            id = tvdb   
        elif imdb != None and imdb != '' and imdb != '0' and imdb != 'None': 
            type = 'imdb'
            id = imdb
        elif tmdb != None and tmdb != '' and tmdb != '0' and tmdb != 'None': 
            type = 'tmdb'
            id = tmdb   
            

        cursor = _get_connection_cursor_meta()
        cursor.execute("SELECT * FROM tv WHERE %s = '%s'" % (type, id))
        row = cursor.fetchone()
        meta = {}
        for id in list(row.keys()): meta[id] = row[id]
        return meta
        #print(("[METALIBRARY] >>> ", meta))
    except:
        return
        
def playcountMeta(type, meta, action=None):
    DBFile = control.playcountDB
    #print ("NEW PLAYCOUNTMETA", DBFile, meta)
    dbcur = _get_connection_cursor_playcount()
    try:
        if type == 'movie':
            
            try: imdb = meta['imdb']
            except: imdb = None
        
            try: tmdb = meta['tmdb']
            except: tmdb = None
            
            if imdb == '' or imdb == 'None' or imdb == None or imdb == '0': imdb = '0'
            if tmdb == '' or tmdb == 'None' or tmdb == None or tmdb == '0': tmdb = '0'
            if imdb == '0' and tmdb == '0': return
            #print ("CREATING MOVIE FILES")

            try:

                dbcur.execute("CREATE TABLE IF NOT EXISTS movies (imdb TEXT, tmdb TEXT, playcount TEXT, UNIQUE(imdb, tmdb, playcount))")
            except Exception (e):
            
                #print ("DATABASE ERROR")

                pass
            if action != None:
                #print(("INSERTING DB", imdb, tmdb, action))
                try:
                    if imdb   != '0': dbcur.execute("DELETE FROM movies WHERE imdb = '%s'" % (imdb))
                    elif tmdb != '0': dbcur.execute("DELETE FROM movies WHERE tmdb = '%s'" % (tmdb))
                    dbcur.execute("INSERT INTO movies Values (?, ?, ?)", (imdb, tmdb, str(action)))
                    dbcur.connection.commit()
                except:
                    label = "[MOVIE][ERROR ADDING]"
                    #print (label)
            else:
                #print ("GETTING PLAYCOUNT DATABASE")
                if imdb   != '0': dbcur.execute("SELECT * FROM movies WHERE imdb = '%s'" % (imdb))
                elif tmdb != '0': dbcur.execute("SELECT * FROM movies WHERE tmdb = '%s'" % (tmdb))
                match = dbcur.fetchone()
                if match is None: return '6'
                playcount = str(match['playcount'])                
                return playcount

            
        if type == 'tv':
            
            try: imdb = meta['imdb']
            except: imdb = '0'
            
            try: tvdb = meta['tvdb']
            except: imdb = '0'
            
            try: tmdb = meta['tmdb']
            except: tmdb = '0'
            if imdb == '' or imdb == 'None' or imdb == None or imdb == '0': imdb = '0'
            if tmdb == '' or tmdb == 'None' or tmdb == None or tmdb == '0': tmdb = '0'
            if tvdb == '' or tvdb == 'None' or tvdb == None or tvdb == '0': tvdb = '0'
            if tvdb == '0' and imdb == '0' and tmdb == '0': return

            try:
                dbcur.execute("CREATE TABLE IF NOT EXISTS tv (imdb TEXT, tvdb TEXT, tmdb TEXT, playcount TEXT, UNIQUE(imdb, tvdb, playcount))")
            except:pass
            
            if action != None:  
                try:
                    label = "[TVSHOW][ADDED]"
                    #print (label)
                    if tvdb   != '0': dbcur.execute("DELETE FROM tv WHERE tvdb = '%s'" % (tvdb))
                    elif imdb != '0': dbcur.execute("DELETE FROM tv WHERE imdb = '%s'" % (imdb))
                    elif tmdb != '0': dbcur.execute("DELETE FROM tv WHERE tmdb = '%s'" % (tmdb))
                    dbcur.execute("INSERT INTO tv Values (?, ?, ?, ?)", (imdb, tvdb, tmdb, str(action)))
                    dbcur.connection.commit()
                except:
                    label = "[TVSHOW][ERROR ADDING]"
                    #print (label)           
            else:

                if tvdb   != '0': dbcur.execute("SELECT * FROM tv WHERE tvdb = '%s'" % (tvdb))
                elif imdb != '0': dbcur.execute("SELECT * FROM tv WHERE imdb = '%s'" % (imdb))
                elif tmdb != '0': dbcur.execute("SELECT * FROM tv WHERE tmdb = '%s'" % (tmdb))
                                                
                match = dbcur.fetchone()
                if match is None: return '6'
                playcount = str(match['playcount'])                
                return playcount

            
        if type == 'episode':
            try: imdb = meta['imdb']
            except: imdb = '0'
            
            try: tvdb = meta['tvdb']
            except: imdb = '0'
            
            try: tmdb = meta['tmdb']
            except: tmdb = '0'
            
            season = "%02d" % int(meta['season'])
            episode = "%02d" % int(meta['episode'])
            if imdb == '' or imdb == 'None' or imdb == None or imdb == '0': imdb = '0'
            if tmdb == '' or tmdb == 'None' or tmdb == None or tmdb == '0': tmdb = '0'
            if tvdb == '' or tvdb == 'None' or tvdb == None or tvdb == '0': tvdb = '0'
            if tvdb == '0' and imdb == '0' and tmdb == '0': return
            

            try:
                dbcur.execute("CREATE TABLE IF NOT EXISTS episodes (imdb TEXT, tvdb TEXT, tmdb TEXT, season TEXT, episode TEXT, playcount TEXT, UNIQUE(imdb, tvdb, season, episode, playcount))")
            except:pass
            
            if action != None:  
                try:
                    label = "[EPISODE][ADDED]"
                    #print (label)
                    if tvdb   != '0': dbcur.execute("DELETE FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
                    elif imdb != '0': dbcur.execute("DELETE FROM episodes WHERE imdb = '%s' and season = '%s' and episode = '%s'" % (imdb, season, episode))
                    elif tmdb != '0': dbcur.execute("DELETE FROM episodes WHERE tmdb = '%s' and season = '%s' and episode = '%s'" % (tmdb, season, episode))
                    
                    dbcur.execute("INSERT INTO episodes Values (?, ?, ?, ?, ?, ?)", (imdb, tvdb, tmdb, season, episode, str(action)))
                    dbcur.connection.commit()
                except:
                    label = "[EPISODE][ERROR ADDING]"
                    #print (label)           
            else:

                if tvdb   != '0': dbcur.execute("SELECT * FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
                elif imdb != '0': dbcur.execute("SELECT * FROM episodes WHERE imdb = '%s' and season = '%s' and episode = '%s'" % (imdb, season, episode))
                elif tmdb != '0': dbcur.execute("SELECT * FROM episodes WHERE tmdb = '%s' and season = '%s' and episode = '%s'" % (tmdb, season, episode))
                match = dbcur.fetchone()
                if match is None: return '6'
                playcount = str(match['playcount'])                
                return playcount

    except:
        return '6'

        


