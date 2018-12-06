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

import re,urllib,urlparse,os
from modules import control
try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database


def metaMovies(imdb):
	try:
		DBASE = control.metaDB
		#print ("META LIBRARY MOVIES PATH", DBASE)
		dbcon = database.connect(DBASE)
		dbcur = dbcon.cursor()
		sources = []
		dbcur.execute("SELECT * FROM movies WHERE imdb = '%s'" % (imdb))
		match = dbcur.fetchone()
		tmdb = str(match[0])
		imdb = str(match[1])
		poster = str(match[3]) 
		fanart = str(match[4]) 
		poster2 = str(match[5]) 
		fanart2 = str(match[6]) 
		clearlogo = str(match[7]) 
		banner    = str(match[8])
		meta = {'imdb':imdb, 'tmdb':tmdb , 'poster':poster, 'fanart': fanart, 'poster2': poster2, 'fanart2':fanart2, 'clearlogo': clearlogo, 'banner': banner}
		print ("[META LIBRARY] >>> ", meta)
		return meta
	except: 
		return



def metaTV(imdb, tvdb):
	try:
		DBASE = control.metaDB
		#print ("META LIBRARY TV PATH", DBASE)
		dbcon = database.connect(DBASE)
		dbcur = dbcon.cursor()
		sources = []
		if imdb != '0' and imdb!= None: dbcur.execute("SELECT * FROM tv WHERE imdb = '%s'" % (imdb))
		elif tvdb != '0' and tvdb != None: dbcur.execute("SELECT * FROM tv WHERE tvdb = '%s'" % (tvdb))
		else: raise Exception()
		match = dbcur.fetchone()
		tmdb = str(match[0])
		imdb = str(match[1])
		try: poster = str(match[4])
		except: poster = '0'
		try: fanart = str(match[5]) 
		except: fanart = '0'
		try: poster2 = str(match[6])
		except: poster2 = '0'
		try: fanart2 = str(match[7])
		except: fanart2 = '0'
		try: poster3 = str(match[8])
		except: poster3 = '0'
		try: fanart3 = str(match[9])
		except: fanart3 = '0'

		try: clearlogo = str(match[10])
		except: clearlogo = '0'
		try: banner = str(match[11])
		except: banner = '0'		
		meta = {'imdb':imdb, 'tvdb':tvdb, 'tmdb':tmdb, 'poster':poster, 'fanart': fanart, 'poster2': poster2, 'fanart2':fanart2, 'poster3': poster3, 'fanart3': fanart3, 'banner': banner, 'clearlogo': clearlogo}
		print ("[META LIBRARY TV] >>> ", meta)
		return meta
	except:
		return
		
def playcountMeta(type, meta, action=None):
    DBFile = control.playcountDB
    if not os.path.exists(DBFile): file(DBFile, 'w').close()
    try:
        if type == 'movie':
            
            imdb = meta['imdb']
            tmdb = meta['tmdb']
            if imdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS movies (""imdb TEXT, ""tmdb TEXT, ""playcount TEXT, ""UNIQUE(imdb, tmdb, playcount)"");")
            except:pass
            if action != None:
				print ("INSERTING DB", imdb, tmdb, action)
				try:
					dbcur.execute("DELETE FROM movies WHERE imdb = '%s'" % (imdb))
					dbcur.execute("INSERT INTO movies Values (?, ?, ?)", (imdb, tmdb, str(action)))
					dbcon.commit()
				except:
					label = "[MOVIE][ERROR ADDING]"
					print (label)
            else:
                dbcur.execute("SELECT * FROM movies WHERE imdb = '%s'" % (imdb))
                match = dbcur.fetchone()
                playcount = str(match[2])
                if match is None: return '6'
                else:return playcount

			
        if type == 'tv':
            
            imdb = meta['imdb']
            tvdb = meta['tvdb']
            if tvdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS tv (""imdb TEXT, ""tvdb TEXT, ""playcount TEXT, ""UNIQUE(imdb, tvdb, playcount)"");")
            except:pass
			
            if action != None:	
				try:
					label = "[TVSHOW][ADDED]"
					print (label)
					dbcur.execute("DELETE FROM tv WHERE tvdb = '%s'" % (tvdb))
					dbcur.execute("INSERT INTO tv Values (?, ?, ?)", (imdb, tvdb, str(action)))
					dbcon.commit()
				except:
					label = "[TVSHOW][ERROR ADDING]"
					print (label)			
            else:

                dbcur.execute("SELECT * FROM tv WHERE tvdb = '%s'" % (tvdb))
                match = dbcur.fetchone()
                playcount = str(match[2])
                if match is None: return '6'
                else:
                    print ("[TVSHOW][IN DATABASE]")
                    return playcount

			
        if type == 'episode':
            imdb = meta['imdb']            
            tvdb = meta['tvdb']
            season = meta['season']
            episode = meta['episode']
            if tvdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS episodes (""imdb TEXT, ""tvdb TEXT,""season TEXT, ""episode TEXT, ""playcount TEXT, ""UNIQUE(imdb, tvdb, season, episode, playcount)"");")
            except:pass
			
            if action != None:	
				try:
					label = "[EPISODE][ADDED]"
					print (label)
					dbcur.execute("DELETE FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
					dbcur.execute("INSERT INTO episodes Values (?, ?, ?, ?, ?)", (imdb, tvdb, season, episode, str(action)))
					dbcon.commit()
				except:
					label = "[EPISODE][ERROR ADDING]"
					print (label)			
            else:

                dbcur.execute("SELECT * FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
                match = dbcur.fetchone()
                playcount = str(match[4])
                if match is None: return '6'
                else:
                    print ("[EPISODE][IN DATABASE]", playcount)
                    return playcount

    except:
        return '6'

		


