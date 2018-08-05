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
		moviesDB = control.moviesDB
		dbcon = database.connect(moviesDB)
		dbcur = dbcon.cursor()
		sources = []
		dbcur.execute("SELECT * FROM movies WHERE imdb = '%s'" % (imdb))
		match = dbcur.fetchone()
		imdb = str(match[0])
		tmdb = str(match[1])
		poster = str(match[2]) 
		fanart = str(match[3]) 
		ftvposter = str(match[4]) 
		ftvfanart = str(match[5]) 
		meta = {'poster':poster, 'fanart': fanart, 'imdb':imdb, 'tmdb':tmdb ,'ftvposter':ftvposter, 'ftvfanart':ftvfanart}
		print ("[META LIBRARY] >>> ", meta)
		return meta
	except: 
		return



def metaTV(imdb,tvdb):
	try:
		tvDB = control.tvDB
		dbcon = database.connect(tvDB)
		dbcur = dbcon.cursor()
		sources = []
		dbcur.execute("SELECT * FROM tv WHERE imdb = '%s' or tvdb ='%s'" % (imdb, tvdb))
		match = dbcur.fetchone()
		tmdb = str(match[2])
		try: poster = str(match[3])
		except: poster = '0'
		try: fanart = str(match[4]) 
		except: fanart = '0'
		try: tvdbposter = str(match[5])
		except: tvdbposter = '0'
		try: tvdbfanart = str(match[6])
		except: tvdbfanart = '0'
		meta = {'poster':poster, 'fanart': fanart, 'tmdb':tmdb, 'tvdbposter':tvdbposter, 'tvdbfanart':tvdbfanart}
		print ("[META LIBRARY] >>> ", meta)
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

		


