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


import json

from resources.lib.modules import control
from resources.lib.api import trakt
from metalibrary import playcountMeta



def traktscrobblePlayback(action, type, imdb = None, tvdb = None, season = None, episode = None, progress = 0):
    try:
        if control.setting('trakt.scrobblePlayback') == 'false': raise Exception()
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        result = trakt.scrobblePlayback(action, type, imdb = imdb, tvdb = tvdb, season = season, episode = episode, progress = progress)
    except: pass
		
def traktPlayback(type, imdb = None, tvdb = None, season = None, episode = None):
    try:
        if control.setting('trakt.scrobblePlayback') == 'false': raise Exception()
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        result = trakt.returnPlayback(type, imdb = imdb, tvdb = tvdb, season = season, episode = episode)
        return result
    except: pass

	
def getMovieIndicators(refresh=False):
    try:
        if trakt.getTraktIndicatorsInfo() == True: raise Exception()
        indicators = playcountMeta
        return indicators
    except:
        pass
    try:
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if refresh == False: timeout = 720
        elif trakt.getWatchedActivity() < trakt.timeoutsyncMovies(): timeout = 720
        else: timeout = 0
        indicators = trakt.cachesyncMovies(timeout=timeout)
        return indicators
    except:
        pass


def getTVShowTraktToLibrary():
    try:
        indicators = trakt.cachesyncTVShowsToLibrary()
        return indicators
    except:
        pass		
		
def getMovieTraktToLibrary():
    try:
        indicators = trakt.cachesyncMoviesToLibrary()
        return indicators
    except:
        pass		
				
	
def getTVShowIndicators(refresh=False):
    try:
        if trakt.getTraktIndicatorsInfo() == True: raise Exception()
        indicators = playcountMeta
        return indicators
    except:
        pass
    try:
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if refresh == False: timeout = 720
        elif trakt.getWatchedActivity() < trakt.timeoutsyncTVShows(): timeout = 720
        else: timeout = 0
        indicators = trakt.cachesyncTVShows(timeout=timeout)
        return indicators
    except:
        pass


def getSeasonIndicators(imdb):
    try:
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        indicators = trakt.syncSeason(imdb)
        return indicators
    except:
        pass


def getMovieOverlay(indicators, imdb):
    try:
        try:
            meta = {'imdb':imdb, 'tmdb':imdb}
            playcount = indicators('movie', meta)
            return str(playcount)
        except:
            playcount = [i for i in indicators if i == imdb]
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '6'
		
def getMoviesOverlayLibrary(indicators, imdb):
    try:
            playcount = [i[2] for i in indicators if i[0] == imdb or i[1] == imdb]
            playcount = playcount[0] if len(playcount) > 0 else []
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '0'


def getTVShowOverlay(indicators, tvdb):
    try:
        try:
            meta = {'imdb':tvdb, 'tvdb':tvdb}
            playcount = indicators('tv', meta)
            return str(playcount)
        except:
			playcount = [i[0] for i in indicators if i[0] == tvdb and len(i[2]) >= int(i[1])]
			playcount = 7 if len(playcount) > 0 else 6
			return str(playcount)
    except:
        return '6'

		
def getEpisodeOverlayLibrary(indicators, imdb, season, episode):

    try:

            playcount = [i[1] for i in indicators if i[0] == imdb]
            playcount = playcount[0] if len(playcount) > 0 else []
            playcount = [i for i in playcount if int(season) == int(i[0]) and int(episode) == int(i[1])]
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '0'

def getEpisodeOverlay(indicators, imdb, tvdb, season, episode):
    try:
        try:
            meta = {'imdb':imdb, 'tvdb':tvdb, 'season': season, 'episode':episode}
            playcount = indicators('episode', meta)
            return str(playcount)
        except:
            playcount = [i[2] for i in indicators if i[0] == tvdb]
            playcount = playcount[0] if len(playcount) > 0 else []
            playcount = [i for i in playcount if int(season) == int(i[0]) and int(episode) == int(i[1])]
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '6'


def markMovieDuringPlayback(imdb, watched):
    try:
        if not control.setting('trakt.scrobbleMovies') == 'true': raise Exception()	
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markMovieAsWatched(imdb)
        else: trakt.markMovieAsNotWatched(imdb)
        trakt.cachesyncMovies()
        # if trakt.getTraktAddonMovieInfo() == True:
            # trakt.markMovieAsNotWatched(imdb)
    except:
        pass

    try:
        type = 'movie'
        action = str(watched)
        meta = {'imdb': imdb, 'tmdb':imdb} 
        playcountMeta(type, meta, action)
    except:
        pass


def markEpisodeDuringPlayback(imdb, tvdb, season, episode, watched):
    try:
        if not control.setting('trakt.scrobbleTV') == 'true': raise Exception()	
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markEpisodeAsWatched(tvdb, season, episode)
        else: trakt.markEpisodeAsNotWatched(tvdb, season, episode)
        trakt.cachesyncTVShows()

        # if trakt.getTraktAddonEpisodeInfo() == True:
            # trakt.markEpisodeAsNotWatched(tvdb, season, episode)
			
    except:
        pass

    try:
        meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
        playcountMeta('episode', meta, str(watched))
    except:
        pass



def movies(imdb, watched):
    # control.busy()
    try:
        if not control.setting('trakt.scrobbleMovies') == 'true': raise Exception()	
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markMovieAsWatched(imdb)
        else: trakt.markMovieAsNotWatched(imdb)
        trakt.cachesyncMovies()
    except:
        pass

    try:
        type = 'movie'
        action = str(watched)
        meta = {'imdb': imdb, 'tmdb':imdb} 
        playcountMeta(type, meta, action)
    except:
        pass


def episodes(imdb, tvdb, season, episode, watched):

    try:
	
        if not control.setting('trakt.scrobbleTV') == 'true': raise Exception()	
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markEpisodeAsWatched(tvdb, season, episode)
        else: trakt.markEpisodeAsNotWatched(tvdb, season, episode)
        trakt.cachesyncTVShows()
        	
    except:
        pass

    try:
        meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
        playcountMeta('episode', meta, str(watched))
    except:
        pass


def tvshows(tvshowtitle, imdb, tvdb, season, watched):

	# #### seasonID 0 is Full Tv Show #####
    SeasonID = str(season)
    try:
        import sys,xbmc
        name = control.addonInfo('name')
        dialog = control.progressDialogBG
        dialog.create(str(name), str(tvshowtitle))
        dialog.update(0, str(name), str(tvshowtitle))
        from resources.lib.indexers import episodes

        year = ''
        items = episodes.episodes().getLibrary(tvshowtitle, year, imdb, tvdb, idx=True)

        if SeasonID == '0':
			metaShow = {'imdb':imdb, 'tvdb':tvdb}
			playcountMeta('tv', metaShow, str(watched))

			try: items = [i for i in items]
			except: pass
			items = [{'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode']))} for i in items]
			for i in range(len(items)):
				if xbmc.abortRequested == True: return sys.exit()
				season, episode = items[i]['season'], items[i]['episode']
				dialog.update(int((100 / float(len(items))) * i), 'Setting MetaData', 'Season: ' + str(season) + ' Episode: ' + str(episode))
				meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
				playcountMeta('episode', meta, str(watched))
        else:
			try: items = [i for i in items if int('%01d' % int(season)) == int('%01d' % int(i['season']))]
			except: pass
			items = [{'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode']))} for i in items]
			
			for i in range(len(items)):
				if xbmc.abortRequested == True: return sys.exit()
				season, episode = items[i]['season'], items[i]['episode']
				dialog.update(int((100 / float(len(items))) * i), 'Setting MetaData', 'Season: ' + str(season) + ' Episode: ' + str(episode))
				meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
				playcountMeta('episode', meta, str(watched))

        try: dialog.close()
        except: pass

    except:
        try: dialog.close()
        except: pass


    try:
        name = control.addonInfo('name')
        dialog = control.progressDialogBG
        dialog.create(str(name), str(tvshowtitle))
        dialog.update(0, str(name), str(tvshowtitle))
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if not control.setting('trakt.scrobbleTV') == 'true': raise Exception()	
        if SeasonID == '0':
            year = ''
            items = episodes.episodes().getLibrary(tvshowtitle, year, imdb, tvdb, idx=True)
            for i in range(len(items)):
				season, episode = items[i]['season'], items[i]['episode']
				dialog.update(int((100 / float(len(items))) * i), 'TRAKT  Watchlist', 'Season: ' + str(season) + ' Episode: ' + str(episode))
				if int(watched) == 7: trakt.markEpisodeAsWatched(tvdb, season, episode)
				else: trakt.markEpisodeAsNotWatched(tvdb, season, episode)
        else:
           year = ''
           items = episodes.episodes().getLibrary(tvshowtitle, year, imdb, tvdb, idx=True)
           items = [(int(i['season']), int(i['episode'])) for i in items]
           items = [i[1] for i in items if int('%01d' % int(season)) == int('%01d' % i[0])]
           for i in items:
			dialog.update(int((100 / float(len(items))) * i), 'TRAKT  Watchlist', 'Season: ' + str(season) + ' Episode: ' + str(i))
			if int(watched) == 7: trakt.markEpisodeAsWatched(tvdb, season, i)
			else: trakt.markEpisodeAsNotWatched(tvdb, season, i)
				
        try: dialog.close()
        except: pass
        trakt.cachesyncTVShows()
    except:
        pass

    # control.refresh()


