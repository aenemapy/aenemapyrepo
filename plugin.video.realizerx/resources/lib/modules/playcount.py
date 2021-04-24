import json
from resources.lib.modules import control
from resources.lib.api import trakt
from resources.lib.modules.metalibrary import playcountMeta
from resources.lib.modules import metalibrary

from resources.lib.modules.log_utils import log
def clearPlaycount():
    clear = metalibrary.clearPlaycount()
    if clear: control.infoDialog('Database Cleared...')

def traktscrobblePlayback(action, type, imdb = None, tvdb = None, tmdb = None, season = None, episode = None, progress = 0):
    try:
        if control.setting('trakt.scrobblePlayback') == 'false': raise Exception()
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        #print(("TRAKT SCROBBLE PLAYBACK",  type, imdb , tvdb, tmdb, season, episode, progress))
        result = trakt.scrobblePlayback(action, type, imdb = imdb, tvdb = tvdb, tmdb = tmdb, season = season, episode = episode, progress = progress)
    except:
        pass
        
def traktPlayback(type, imdb = None, tvdb = None, tmdb = None, season = None, episode = None):
    try:
        if control.setting('trakt.scrobblePlayback') == 'false': raise Exception()
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        result = trakt.returnPlayback(type, imdb = imdb, tvdb = tvdb, tmdb = tmdb, season = season, episode = episode)
        return result
    except:
        return 0



def getMovieIndicators(refresh=False):
    try:
        if trakt.getTraktIndicatorsInfo() == True: raise Exception()
        indicators = playcountMeta
        return indicators
    except:
        pass
    try:
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        print ("TRAKT MOVIES")
        if refresh == False: timeout = 720
        elif int(trakt.getWatchedActivity()) < int(trakt.timeoutsyncMovies()): timeout = 720
        else: timeout = 0
        print ("TRAKT TIMEOUT", timeout)
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


def getMoviesOverlayLibrary(indicators, imdb):
    try:
        playcount = [i[2] for i in indicators if i[0] == imdb or i[1] == imdb]
        playcount = playcount[0] if len(playcount) > 0 else []
        playcount = 7 if len(playcount) > 0 else 6
        return str(playcount)
    except:
        return '0'

        
def getEpisodeOverlayLibrary(indicators, imdb, season, episode):
    try:
        playcount = [i[1] for i in indicators if i[0] == imdb]
        playcount = playcount[0] if len(playcount) > 0 else []
        playcount = [i for i in playcount if int(season) == int(i[0]) and int(episode) == int(i[1])]
        playcount = 7 if len(playcount) > 0 else 6
        return str(playcount)
    except:
        return '0'

# MAIN MARKINGS
def getMovieOverlay(indicators, imdb=None, tmdb=None, traktOnly=False):
    try:
        try: # DATABASE
            #print ("GETTING MOVIE OVERLAY")
            if traktOnly == True: raise Exception()
            meta = {'imdb':imdb, 'tmdb': tmdb}
            playcount = indicators('movie', meta)
            return str(playcount)
        except: # TRAKT
            if imdb != None and imdb != '0':
                playcount = [i for i in indicators if str(i[0]) == str(imdb)]
            elif tmdb != None and tmdb != '0':
                playcount = [i for i in indicators if str(i[1]) == str(tmdb)]       
            
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '6'
        
        
def getTVShowOverlay(indicators, tvdb=None, imdb=None, tmdb=None):
    try:
        try: # DATABASE
            meta = {'imdb': imdb, 'tmdb': tmdb}
            playcount = indicators('tv', meta)
            return str(playcount)
        except: # TRAKT
            if tvdb != None and tvdb != '0':
                playcount = [i for i in indicators if str(i[2]) == str(tvdb) and len(i[4]) >= int(i[3])]
            elif imdb != None and imdb != '0':
                playcount = [i for i in indicators if str(i[0])  == str(imdb) and len(i[4]) >= int(i[3])]
            elif tmdb != None and tmdb != '0':
                playcount = [i for i in indicators if str(i[1]) == str(tmdb) and len(i[4]) >= int(i[3])]
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '6'

def getEpisodeOverlay(indicators, season, episode, imdb=None, tmdb=None, tvdb=None, traktOnly=False):
    try:
        try: # DATABASE
            if  traktOnly == True: raise Exception()
            meta = {'imdb':imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'season': season, 'episode':episode}
            playcount = indicators('episode', meta)
            return str(playcount)
        except: # TRAKT
            if tvdb != None and tvdb != '0':
                playcount = [i[4] for i in indicators if str(i[2]) == str(tvdb)]
            elif imdb != None and imdb != '0':
                playcount = [i[4] for i in indicators if str(i[0]) == str(imdb)]
            elif tmdb != None and tmdb != '0':
                playcount = [i[4] for i in indicators if str(i[1]) == str(tmdb)]    
            #for i in indicators: #print ("INDICATOR", i[0], i[1], i[2], i[3], i[4])

            playcount = playcount[0] if len(playcount) > 0 else []
            playcount = [i for i in playcount if int(season) == int(i[0]) and int(episode) == int(i[1])]
            playcount = 7 if len(playcount) > 0 else 6
            return str(playcount)
    except:
        return '6'

# MAIN MARK CALLS
def markMovieDuringPlayback(watched , imdb=None, tmdb=None,  refresh=False):
    try:
        if not control.setting('trakt.scrobbleMovies') == 'true': raise Exception() 
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        
        if int(watched) == 7: 
            # AVOID DUPLICATE WATCHING
            indicators = getMovieIndicators(refresh=True)
            overlay = int(getMovieOverlay(indicators, imdb=imdb, tmdb=tmdb, traktOnly=True))
            if overlay == 7: raise Exception()
            
            trakt.markMovieAsWatched(imdb=imdb, tmdb=tmdb)
        else: 

            trakt.markMovieAsNotWatched(imdb=imdb, tmdb=tmdb)
        trakt.cachesyncMovies()
    except:
        pass
    try:
        type = 'movie'
        action = str(watched)
        meta = {'imdb': imdb, 'tmdb': tmdb} 
        playcountMeta(type, meta, action)
    except:
        pass
    if refresh== True: control.refresh()




def markEpisodeDuringPlayback(season, episode, watched, imdb=None, tmdb=None, tvdb=None, refresh=False):
    try:
        if not control.setting('trakt.scrobbleTV') == 'true': raise Exception() 
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()

        if int(watched) == 7: 
            # AVOID WATCHING DUPLICATES
            indicators = getTVShowIndicators(refresh=True)
            overlay = int(getEpisodeOverlay(indicators, season, episode, imdb=imdb, tmdb=tmdb, tvdb=tvdb, traktOnly=True))
            if overlay == 7: raise Exception()
            trakt.markEpisodeAsWatched(season, episode, imdb=imdb, tmdb=tmdb, tvdb=tvdb)
        else: trakt.markEpisodeAsNotWatched(season, episode, imdb=imdb, tmdb=tmdb, tvdb=tvdb)
        trakt.cachesyncTVShows()
    except:
        pass

    try:
        meta = {'imdb':imdb, 'tvdb':tvdb, 'tmdb': tmdb, 'season':season, 'episode':episode}
        playcountMeta('episode', meta, str(watched))
    except:
        pass

        
    if refresh== True: control.refresh()

def movies(watched, imdb=None, tmdb=None):
    try:
        if not control.setting('trakt.scrobbleMovies') == 'true': raise Exception()
        print("trakt indicators")
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markMovieAsWatched(imdb=imdb, tmdb=tmdb)
        else: trakt.markMovieAsNotWatched(imdb=imdb, tmdb=tmdb)
        trakt.cachesyncMovies()
    except:
        pass

    try:
        type = 'movie'
        action = str(watched)
        meta = {'imdb': imdb, 'tmdb': tmdb} 
        playcountMeta(type, meta, action)
    except:
        pass


def episodes(season, episode, watched, imdb=None, tvdb=None, tmdb=None):

    try:
    
        if not control.setting('trakt.scrobbleTV') == 'true': raise Exception() 
        if trakt.getTraktIndicatorsInfo() == False: raise Exception()
        if int(watched) == 7: trakt.markEpisodeAsWatched(season, episode, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
        else: trakt.markEpisodeAsNotWatched(season, episode, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
        trakt.cachesyncTVShows()
            
    except:
        pass

    try:
        meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
        playcountMeta('episode', meta, str(watched))
    except:
        pass



def tvshows(tvshowtitle, season, watched, imdb=None, tvdb=None, tmdb=None):
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
        library = episodes.episodes().getLibrary(tvshowtitle, year, imdb, tvdb, idx=True)

        if SeasonID == '0':
            metaShow = {'imdb':imdb, 'tvdb':tvdb}
            playcountMeta('tv', metaShow, str(watched))

            try: items = [i for i in library]
            except: pass
            items = [{'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode']))} for i in items]
            for i in range(len(items)):
                if xbmc.abortRequested == True: return sys.exit()
                season, episode = items[i]['season'], items[i]['episode']
                dialog.update(int((100 / float(len(items))) * i), 'Setting MetaData', 'Season: ' + str(season) + ' Episode: ' + str(episode))
                meta = {'imdb':imdb, 'tvdb':tvdb, 'season':season, 'episode':episode}
                playcountMeta('episode', meta, str(watched))

                
                
        else:
            try: items = [i for i in library if int('%01d' % int(season)) == int('%01d' % int(i['season']))]
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
            for i in range(len(library)):
                season, episode = items[i]['season'], items[i]['episode']
                dialog.update(int((100 / float(len(items))) * i), 'TRAKT Watch Status', 'Season: ' + str(season) + ' Episode: ' + str(episode))
                if int(watched) == 7: trakt.markEpisodeAsWatched(season, episode, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
                else: trakt.markEpisodeAsNotWatched(season, episode, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
        else:
           year = ''
           items = [(int(i['season']), int(i['episode'])) for i in library]
           items = [i[1] for i in items if int('%01d' % int(season)) == int('%01d' % i[0])]
           for i in items:
            dialog.update(int((100 / float(len(items))) * i), 'TRAKT Watch Status', 'Season: ' + str(season) + ' Episode: ' + str(i))
            if int(watched) == 7: trakt.markEpisodeAsWatched(season, i, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
            else: trakt.markEpisodeAsNotWatched(season, i, tvdb=tvdb, imdb=imdb, tmdb=tmdb)
                
        try: dialog.close()
        except: pass
        trakt.cachesyncTVShows()
    except:
        pass


    # control.refresh()


