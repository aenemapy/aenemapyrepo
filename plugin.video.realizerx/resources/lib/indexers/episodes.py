# -*- coding: utf-8 -*-

'''
    solaris Add-on
    Copyright (C) 2016 solaris

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


from resources.lib.api import trakt
from resources.lib.modules import cleantitle
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import playcount
from resources.lib.modules import views
from resources.lib.modules import utils
from resources.lib.modules import metalibrary
from resources.lib.api import tvdbapi, tmdbapi, fanarttv
import libThread
import os,sys,re,json,zipfile,io,urllib.request,urllib.parse,urllib.error,urllib.request,urllib.error,urllib.parse,urllib.parse,datetime,json,time

params = dict(urllib.parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

class seasons:
    def __init__(self):
        self.list = []
        self.poster = ''
        self.fanart = ''
        self.seasons_posters = '0'
        self.episodeList = []
        self.lang = control.apiLanguage()['tvdb']
        
        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone): self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
        else: self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))

        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.tvdb_key = control.setting('tvdb.api')
        if self.tvdb_key == '' or self.tvdb_key == '0' or self.tvdb_key == None: self.tvdb_key = '69F2FCC839393569'
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
        
        
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key, '%s', '%s')
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'

        poster_size = ['w154', 'w500', 'original']
        fanart_size = ['w300', 'w1280', 'original']
        
        poster_quality = poster_size[int(control.setting('poster.type'))]
        fanart_quality = fanart_size[int(control.setting('fanart.type'))]
        
        self.tmdb_image = 'https://image.tmdb.org/t/p/%s'  % fanart_quality
        self.tmdb_poster = 'https://image.tmdb.org/t/p/%s' % poster_quality 
        
        ########### TVDB API 2 #######################      
        self.tvdb2_api = 'https://api.thetvdb.com'
        self.tvdb2_info_series = 'https://api.thetvdb.com/series/%s'
        self.tvdb2_series_poster = 'https://api.thetvdb.com/series/%s/images/query?keyType=poster'  % ('%s')
        self.tvdb2_series_fanart = 'https://api.thetvdb.com/series/%s/images/query?keyType=fanart'  % ('%s')
        self.tvdb2_series_banner = 'https://api.thetvdb.com/series/%s/images/query?keyType=series'  % ('%s')
        self.tvdb2_series_season = 'https://api.thetvdb.com/series/%s/images/query?keyType=season'  % ('%s')
        self.tvdb2_series_bannerseason = 'https://api.thetvdb.com/series/%s/images/query?keyType=seasonwide'    % ('%s')
        self.tvdb2_by_imdb = 'https://api.thetvdb.com/search/series?imdbId=%s'
        self.tvdb2_by_query = 'https://api.thetvdb.com/search/series?name=%s'
        self.tvdb2_series_actors = 'https://api.thetvdb.com/series/%s/actors'   % ('%s')        
        self.tvdb2_episodes = 'https://api.thetvdb.com/series/%s/episodes'  % ('%s')    
        self.tvdb2_get_episode = 'https://api.thetvdb.com/episodes/%s'
        self.tvdb2_episodes_summary = 'https://api.thetvdb.com/series/%s/episodes/summary'  % ('%s')


    def nextepisode(self, tvshowtitle, year, imdb, tvdb, lang, season, episode):
        self.list = cache.get(self.tvdb_list, 24, tvshowtitle, year, imdb, tvdb, 'en', season, episode, None, 'nextepisode')
        return self.list

        
    def getTMDB(self, tvshowtitle, year, imdb, tvdb, tmdb, limit='seasons'):
        try:
            self.list =cache.get(self.tmdb_list, 24, tvshowtitle, year, imdb, tvdb, tmdb, None, 'seasons')
            self.seasonDirectory(self.list)
            return self.list
        except:
            pass
    
    
    def get(self, tvshowtitle, year, imdb, tvdb, idx=True, create_directory=True):
        if control.window.getProperty('PseudoTVRunning') == 'True':
            return episodes().get(tvshowtitle, year, imdb, tvdb)

        if idx == True:
            self.list = cache.get(self.tvdb_list, 24, tvshowtitle, year, imdb, tvdb, 'en', None, None, None, 'seasons')
            if create_directory == True: self.seasonDirectory(self.list)
            return self.list
        else:
            self.list = cache.get(self.tvdb_list, 24, tvshowtitle, year, imdb, tvdb, 'en' , None, None, None, 'seasons')
            return self.list

    def tmdb_list(self, tvshowtitle, year, imdb, tvdb, tmdb, season=None, episode=None, limit='seasons'):

        item = cache.get(tmdbapi.getDetails, 0, tmdb, True)  
       
        poster = item['poster_path']
        poster = self.tmdb_poster + poster
        
        fanart = item['backdrop_path']
        fanart = self.tmdb_image + fanart
        plot = item['overview']
        try:
            duration = item.get('episode_run_time')
            duration = duration[0]
        except:
            duration = '0'
            duration = str(duration)   

            
        if limit == 'seasons':
            
            jsonS = item['seasons']
            for seasonDetails in jsonS:
                try:
                    sName      = seasonDetails['name']
                    sPoster    = seasonDetails['poster_path']
                    sPremiered = seasonDetails['air_date']
                    sID        = seasonDetails['season_number']
                    
                    self.list.append({'tmdbMeta': True, 'poster': self.tmdb_poster + sPoster, 'season': str(sID), 'fanart': fanart, 'plot': plot, 'premiered': sPremiered, 'title': sName, 'originaltitle': sName, 'tvshowtitle': tvshowtitle, 'year': year, 'tmdb': tmdb, 'tvdb': tvdb, 'imdb': imdb})
                except:pass
        elif limit == 'episodes':
            item = cache.get(tmdbapi.getEpisodes, 24, tmdb, season) 
            jsonEps = item['episodes']
            for epDetails in jsonEps:
                try:
                    ##print ("TMDB epDetails 1",epDetails)
                    epName      = epDetails['name']

                    epPlot      = epDetails['overview']

                    premiered   = epDetails['air_date']

                    epID        = epDetails['episode_number']

                    try:
                        thumb       = epDetails['still_path']
                        thumb       = self.tmdb_image + thumb   
                    except: thumb = '0'
                
                    try: rating      = epDetails['vote_average']
                    except: rating = '0'

                    try: votes       = epDetails['vote_count']
                    except: votes = '0'

                                                
                    meta = {'tmdbMeta': True, 'rating': str(rating), 'votes': str(votes), 'thumb': thumb, 'poster': poster, 'season': season, 'episode': str(epID), 'fanart': fanart, 'plot': epPlot, 'premiered': premiered, 'title': epName, 'duration': duration, 'originaltitle': epName, 'tvshowtitle': tvshowtitle, 'year': year, 'tmdb': tmdb, 'tvdb': tvdb, 'imdb': imdb}
                    self.list.append(meta)

                except:pass         
        elif limit == 'nextepisode':
            # i['tvshowtitle'], i['year'], i['imdb'], i['tvdb'], i['tmdb'], i['snum'],  i['enum'], 'nextepisode')

            ss = int(season) + 1
            ee = int(episode) + 1
            item = cache.get(tmdbapi.getSingleEp, 24, tmdb, season, ee) 
            checkEp = item['episode_number']

            if checkEp == None:
            
                item = cache.get(tmdbapi.getSingleEp, 24, tmdb, ss, '01') 
            epDetails = item

            try:
                    ##print ("TMDB epDetails 1",epDetails)
                epName      = epDetails['name']

                epPlot      = epDetails['overview']

                premiered   = epDetails['air_date']

                epID        = epDetails['episode_number']

                try:
                    thumb       = epDetails['still_path']
                    thumb       = self.tmdb_image + thumb   
                except: thumb = '0'
                
                try: rating      = epDetails['vote_average']
                except: rating = '0'

                try: votes       = epDetails['vote_count']
                except: votes = '0'

                                                
                meta = {'tmdbMeta': True, 'rating': str(rating), 'votes': str(votes), 'thumb': thumb, 'poster': poster, 'season': season, 'episode': str(epID), 'fanart': fanart, 'plot': epPlot, 'premiered': premiered, 'title': epName, 'duration': duration, 'originaltitle': epName, 'tvshowtitle': tvshowtitle, 'year': year, 'tmdb': tmdb, 'tvdb': tvdb, 'imdb': imdb}
                self.list.append(meta)
            except:pass         
                
        return self.list
        
        
    
    # LIMITS :  "full" = all episodes | "seasons" = Get Season |  "1, 2, 3 etc" = Episodes for a Specific Season
    def tvdb_list(self, tvshowtitle, year, imdb, tvdb, lang, season=None, episode=None, tvdb_epId = None, limit='seasons'):
        try:
            if imdb == '0':
                try:
                    imdb = trakt.SearchTVShow(urllib.parse.quote_plus(tvshowtitle), year, full=False)[0]
                    imdb = imdb.get('show', '0')
                    imdb = imdb.get('ids', {}).get('imdb', '0')
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                    if not imdb: imdb = '0'
                except:
                    imdb = '0'

            if tvdb == '0' and not imdb == '0':
                u = self.tvdb2_by_imdb % imdb
                result = tvdbapi.getTvdb(u)
                item = json.loads(result)
                item = item['data']
                try:    tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(item))[0]
                except: tvdb = ''
                if tvdb == '': tvdb = '0'
                tvdb = tvdb.encode('utf-8')

            if tvdb == '0':
                url = self.tvdb2_by_query % (urllib.parse.quote_plus(self.list[i]['title']))
                result = tvdbapi.getTvdb(url)
                item = json.loads(result)
                item = item['data']
                years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]
                tvdb = [(x, x['seriesName'], x['firstAired']) for x in item]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1]) and any(y in x[2] for y in years)]
                tvdb = [x[0] for x in tvdb][0]
                try:    tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(tvdb))[0]
                except: tvdb = ''
                if tvdb == '': tvdb = '0'
                
        except:
            return

        try:
            if tvdb == '0': return

            # ################ SERIES META ###############################

            s_url = self.tvdb2_info_series % tvdb
            api = tvdbapi.getTvdb(s_url)        
            api = json.loads(api)
            api = api['data']
            
            tvshowtitle = api['seriesName']
            label = tvshowtitle
            try: 
                year = api['firstAired']
                year = re.compile('(\d{4})').findall(year)[0]
            except: year = '0'

            tvdb = str(tvdb)
            imdb = str(imdb)
            
            ##print ("TVDB SEASON LIST", tvdb, tvshowtitle)          
            if imdb == '' or imdb == None or imdb == '0': imdb = api['imdbId']
            #IMAGES
            poster = '0'
            cast = '0'
            self.poster = '0'
            self.fanart = '0'
            self.seasons_posters = '0'
            clearlogo = '0'
            
            try: banner = api['banner']     
            except: banner = '0'
            if banner == '' or banner == None: banner = '0'
            if banner != '0' : banner = self.tvdb_image + banner
            
            getmeta = []

            getmeta.append(libThread.Thread(self.threadPoster, tvdb))
            getmeta.append(libThread.Thread(self.threadFanart, tvdb))
            
            if limit == 'seasons': getmeta.append(libThread.Thread(self.threadSeasons, tvdb))           
            [i.start() for i in getmeta]    
            [i.join() for i in getmeta] 
            
            # for i in range(0,100):
                # try:
                    # time.sleep(0.1)
                    # is_alive = [x for x in getmeta if x.is_alive() == True]
                    # if not is_alive: break
                # except:
                    # pass
            #print(("TVDB SEASON LIST 2", tvdb, tvshowtitle))                        
            try: premiered = api['firstAired'].encode('utf-8')
            except: premiered = '0'
            if premiered == '' or premiered == None: premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = premiered.encode('utf-8')

            try: studio = api['network']
            except: studio = ''
            if studio == '' or studio == None: studio = '0'
            studio = client.replaceHTMLCodes(studio)
            studio = studio.encode('utf-8')

            try: genre = api['genre']
            except: genre = ''
            genre = [x for x in genre]
            genre = ' / '.join(genre)
            if genre == '' or genre == None: genre = '0'
            genre = client.replaceHTMLCodes(genre)
            genre = genre.encode('utf-8')

            #print(("TVDB SEASON LIST 3", tvdb, tvshowtitle))                
            try: duration = api['runtime']
            except: duration = ''
            if duration == '' or duration == None: duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = duration.encode('utf-8')         
            # #print ("TVDB EPISODES duration", duration)    

            try: status = api['status']
            except: status = ''
            if status == '' or status == None: status = '0'
            status = client.replaceHTMLCodes(status)
            status = status.encode('utf-8')

            try: rating = api.get('siteRating')
            except: rating = ''
            if rating == '' or rating == None: rating = '0'
            rating = str(rating)

            rating = rating.encode('utf-8')

            try: votes = api.get('siteRatingCount')
            except: votes = ''
            if votes == '' or votes == None: votes = '0'
                # #print ("TVDB votes", votes)
            #print(("TVDB SEASON LIST 4", tvdb, tvshowtitle))                    
            try: mpaa = api['rating']
            except: mpaa = ''
            if mpaa == '' or mpaa == None: mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = mpaa.encode('utf-8')
            #print(("TVDB SEASON LIST 5", tvdb, tvshowtitle))    
            cast = '0'
            
            try: plot = api['overview']
            except: plot = '0'
            if plot == '' or plot == None: plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot

            threads = []
            seasons = []
            seasonList = []
            self.episodeList = []
            #print(("TVDB SEASON LIST 6", tvdb, tvshowtitle))                            
            if limit == 'full': tvdb_Api = self.tvdb2_episodes_summary % tvdb   
            else: tvdb_Api = self.tvdb2_episodes % tvdb
            ##print ("TVDB SEASON LIST 7", tvdb, tvshowtitle)    
            # NEXT EPISODES         
            if limit == 'nextepisode':

                nextSeason = int(season) + 1
                nextEpisode = int(episode) + 1              
                epquery  = '/query?airedSeason=%s&airedEpisode=%s' % (str(season), str(nextEpisode))
                epquery2 = '/query?airedSeason=%s&airedEpisode=%s' % (str(nextSeason), '1')


                try: 
                    json_tvdb    = tvdbapi.getTvdb(tvdb_Api + epquery)
                    tvdb_data      = json.loads(json_tvdb)
                    tvdb_data      = tvdb_data['data']                  
                    seasonList = [i for i in tvdb_data if str(i['airedEpisodeNumber']) == str(nextEpisode) and str(i['airedSeason']) == str(season)]
                except: pass
                
                try: 
                    if int(len(seasonList)) > 0: raise Exception()
                    json_tvdb    = tvdbapi.getTvdb(tvdb_Api + epquery2)
                    tvdb_data      = json.loads(json_tvdb)
                    tvdb_data      = tvdb_data['data']      
                    seasonList += [i for i in tvdb_data if str(i['airedEpisodeNumber']) == '1' and str(i['airedSeason']) == str(nextSeason)]
                except: pass
                self.episodeList =  seasonList  
                seasons = []

            # SINGLE EPISODE    
            elif limit == 'episode_info':
                if tvdb_epId != None:   # SINGLE EPISODE BASED ON TVDB ID
                    epquery  = '/episodes/%s' % (str(tvdb_epId))
                    json_tvdb    = tvdbapi.getTvdb(self.tvdb2_api + epquery)
                    tvdb_data      = json.loads(json_tvdb)
                    seasonList.append(tvdb_data['data'])
                    self.episodeList =  seasonList          
                    seasons = []                    
                
                else: # SINGLE EPISODE BASED ON SEASON AND EPISODE
                    epquery  = '/query?airedSeason=%s&airedEpisode=%s' % (str(season), str(episode))
                    json_tvdb    = tvdbapi.getTvdb(tvdb_Api + epquery)
                    tvdb_data      = json.loads(json_tvdb)
                    tvdb_data      = tvdb_data['data']  
                    try: seasonList += [i for i in tvdb_data if str(i['airedEpisodeNumber']) == str(episode) and str(i['airedSeason']) == str(season)]
                    except: pass
                    self.episodeList =  seasonList          
                    seasons = []    

            

            # EPISODES for A SPECIFIC SEASON    
            elif limit == 'episodes':
                episodes = "https://api.thetvdb.com/series/%s/episodes/query?airedSeason=%s" % (tvdb, str(season))
                episodes = tvdbapi.getTvdb(episodes)
                episodes = json.loads(episodes)
                episodes = episodes['data'] 
                self.episodeList = episodes
                seasons = []                
            
            #  SEASONS
            elif limit == 'seasons': 
                self.episodeList = []
                result = tvdbapi.getTvdb(tvdb_Api)
                tvdb_req = json.loads(result)
                tvdb_data = tvdb_req['data']
                lastPage = tvdb_req['links']['last']
                
                if int(lastPage) > 1:
                    for i in range(1, int(lastPage)+1):
                        if i != 1: 
                            nextPage = "?page=%s" % i
                            nextPage = tvdb_Api + nextPage
                            json_tvdb = tvdbapi.getTvdb(nextPage)
                            tvdb_req  = json.loads(json_tvdb)
                            tvdb_data += tvdb_req['data']
            
            
                try: seasonList += [i for i in tvdb_data if str(i['airedEpisodeNumber']) == '1' and str(i['airedSeason']) != '0']
                except: pass
                seasonList = sorted(seasonList, key = lambda x : x['airedSeason'])  
                seasons = seasonList    
                
            # FLATTEN EPISODES
            elif limit == 'full':
                seasonList = tvdb_data['airedSeasons']
                seasonList = sorted(seasonList, key = lambda x : int(x))
                seasonList = [i for i in seasonList if not i == '0']
                for season in seasonList:
                    if season == '0': continue
                    url = "https://api.thetvdb.com/series/%s/episodes/query?airedSeason=%s" % (tvdb, str(season))
                    threads.append(libThread.Thread(self.threadEpisodes, url))  
                [i.start() for i in threads]
                [i.join() for i in threads]

        except:
            pass
    
            
        try: seasons_posters = self.seasons_posters
        except: seasons_posters = '0'
            
        for item in seasons:
            ##print ("TVDB LIST seasonList", item)               
            try:
                try: premiered = item['firstAired']
                except: premiered = '0'
                if premiered == '': premiered = '0'
                premiered = client.replaceHTMLCodes(premiered)
                premiered = premiered
                ##print ("TVDB LIST premiered", premiered)   

                season = item.get('airedSeason')
                season = str(season)
                season = season
                if season == '0': continue
                ##print ("TVDB LIST season", season) 

                if not seasons_posters == '0':
                    for thumbs, sid in seasons_posters:
                        if sid == season:
                            thumb = thumbs
                            thumb = self.tvdb_image + thumb
                else: thumb = self.poster
            
                if thumb == '0' or thumb == '' or thumb == None: thumb = self.poster            
                self.list.append({'season': season, 'tvshowtitle': tvshowtitle, 'label': label, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': '0', 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': self.poster, 'clearlogo': clearlogo, 'banner': banner, 'fanart': self.fanart, 'thumb': thumb})
            except:
                pass

        episodelist = []

        try: 
            if limit == 'full': self.episodeList = sorted(self.episodeList, key = lambda x : int(x['airedSeason']))
            else: self.episodeList = sorted(self.episodeList, key = lambda x : int(x['airedEpisodeNumber']))
        except:pass
        
        for item in self.episodeList:
            try:
                id = item.get('id')
                id = str(id)
                id = id

                epnumber = item.get('airedEpisodeNumber')
                epnumber = str(epnumber)
                epnumber = epnumber

                season = item.get('airedSeason')
                season = str(season)
                season = season
                episodelist.append(id)

                try:title = item['episodeName']
                except: title = '0' 

                try:premiered = item['firstAired']
                except: premiered = '0'             
                
                if limit == 'nextepisode':
                    if int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str(self.today_date))): continue
           
                self.list.append({'id': id, 'epnumber' : epnumber, 'title': title,'label': title, 'season': season, 'episode': epnumber, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': self.poster, 'clearlogo': clearlogo, 'banner': banner, 'fanart': self.fanart, 'thumb': self.fanart})

                # self.list.append({'title': title, 'label': label, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': episodeplot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb})
            except:
                pass
                
                
                
        try:
            total = len(episodelist)
            if int(total) > 0: 
                for r in range(0, total, 40):
                    threads = []
                    for i in range(r, r+40):
                        if i <= total: threads.append(libThread.Thread(self.super_info, i))
                    [i.start() for i in threads]
                    [i.join() for i in threads] 
        except: pass                
        ##print ("SOLARIS FINAL LISTS", self.list)
        return self.list
        

    def tvdbLibrary(self, tvshowtitle, year, imdb, tvdb, lang):

        try:
            if imdb == '0':
                try:
                    imdb = trakt.SearchTVShow(urllib.parse.quote_plus(tvshowtitle), year, full=False)[0]
                    imdb = imdb.get('show', '0')
                    imdb = imdb.get('ids', {}).get('imdb', '0')
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                    if not imdb: imdb = '0'
                except:
                    imdb = '0'

            if tvdb == '0' and not imdb == '0':
                
                u = self.tvdb2_by_imdb % imdb
                result = tvdbapi.getTvdb(u)
                item = json.loads(result)
                item = item['data']
                try:    tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(item))[0]
                except: tvdb = ''
                if tvdb == '': tvdb = '0'
                tvdb = tvdb

            if tvdb == '0':
                url = self.tvdb2_by_query % (urllib.parse.quote_plus(self.list[i]['title']))
                result = tvdbapi.getTvdb(url)
                item = json.loads(result)
                item = item['data']
                years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]
                tvdb = [(x, x['seriesName'], x['firstAired']) for x in item]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1]) and any(y in x[2] for y in years)]
                tvdb = [x[0] for x in tvdb][0]
                try:    tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(tvdb))[0]
                except: tvdb = ''
                if tvdb == '': tvdb = '0'
                
        except:
            return


        try:
            if tvdb == '0': return

            # ################ SERIES META ###############################

            label = tvshowtitle
            year = year
            tvdb = tvdb
            imdb = imdb

            tvdb_Api = self.tvdb2_episodes % tvdb   

            result = tvdbapi.getTvdb(tvdb_Api)
            tvdb_req = json.loads(result)
            tvdb_data = tvdb_req['data']
            lastPage = tvdb_req['links']['last']
                
            if int(lastPage) > 1:
                for i in range(1, int(lastPage)+1):
                    if i != 1: 
                        nextPage = "?page=%s" % i
                        nextPage = tvdb_Api + nextPage
                        json_tvdb = tvdbapi.getTvdb(nextPage)
                        tvdb_req  = json.loads(json_tvdb)
                        tvdb_data += tvdb_req['data']
        
            episodes = []
            seasons = [i for i in tvdb_data if str(i['airedEpisodeNumber']) == '1' and not str(i['airedSeason']) == '0']
            seasons = sorted(seasons, key = lambda x : x['airedSeason'])
            
            # episodes = [i for i in tvdbApi]           
            # episodes = sorted(episodes, key = lambda x : x['airedSeason'])
            threads = []        

            
            for item in seasons:
                try:
                    season = item.get('airedSeason')
                    season = str(season)
                    season = season
                    if season == '0': continue
                    url = "https://api.thetvdb.com/series/%s/episodes/query?airedSeason=%s" % (tvdb, str(season))
                    threads.append(libThread.Thread(self.threadEpisodes, url))  
                except:
                        pass
                                    
            [i.start() for i in threads]
            [i.join() for i in threads]                         
            episodes = []
            seasons = []



        except:
            pass
    
            

        for item in self.episodeList:
            
            try:
                id = item.get('id')
                id = str(id)
                id = id
                
                epnumber = item.get('airedEpisodeNumber')
                epnumber = str(epnumber)
                epnumber = epnumber

                season = item.get('airedSeason')
                season = str(season)
                season = season

                try:title = item['episodeName']
                except: title = '0' 

                try:premiered = item['firstAired']
                except: premiered = '0'

                if int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str(self.today_date))): continue
                if control.setting('library.nextday.episodes') == 'true':   
                    if int(re.sub('[^0-9]', '', str(premiered))) == int(re.sub('[^0-9]', '', str(self.today_date))): continue                   
                self.list.append({'id': id, 'epnumber' : epnumber, 'title': title, 'label': label, 'season': season, 'episode': epnumber, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': '0', 'studio': '0', 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': '0', 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'banner': '0', 'fanart': '0', 'thumb': '0'})

                # self.list.append({'title': title, 'label': label, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': episodeplot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb})
            except:
                pass

        return self.list
                
        
    def threadEpisodes(self, url):
        try:
            r = tvdbapi.getTvdb(url)
            r = json.loads(r)
            r = r['data']
            self.episodeList += r
            return self.episodeList
        except:
            pass


            
    def remotedb_meta(self, imdb=None, tmdb=None, tvdb=None):
        try:
            if control.setting('local.meta') != 'true': return None
            dbmeta = metalibrary.metaTV(imdb=imdb, tmdb=tmdb, tvdb=tvdb)
            return dbmeta
            
        except:pass
        
    def threadPoster(self, tvdb):
        try:
            self.remotedbMeta = None
            if self.remotedbMeta != None:
                if len(self.remotedbMeta) > 0: 
                    self.poster = self.tmdb_poster + self.remotedbMeta['poster']
            else:
                try:
                        from resources.lib.api import tmdbapi
                
                        tmdbArt = tmdbapi.getTvdb(tvdb)
                        try: 
                            tmdbArt = json.loads(tmdbArt)
                            tmdbArt = tmdbArt['tv_results'][0]
                        except: artmeta = False
                        
                        try:
                            tmdb = tmdbArt['id']
                            if tmdb == '' or tmdb == None: tmdb = '0'
                        except:
                            pass             
                        try:
                            poster2 = tmdbArt['poster_path']
                            if poster2 != '' and poster2 != '0' and poster2 != None:
                                self.poster = self.tmdb_poster + poster2
                                poster = poster
                        except:
                            pass
                        try:
                            if fanart == '0' or fanart == '' or fanart == None:
                                fanart = tmdbArt['backdrop_path']
                                self.fanart = self.tmdb_image + fanart
                                fanart = fanart
                        except:
                            fanart = '0'    
                except: pass
                
            if self.poster == '' or self.poster == '0' or self.poster == None: self.poster = tvdbapi.getPoster(tvdb)    
            
            
            # #print ("SOLARIS META POSTER", self.poster)
            return self.poster

        except:
            pass
    
    
    def threadFanart(self, tvdb):
        try:
            self.remotedbMeta = None
            if self.remotedbMeta != None:
                if len(self.remotedbMeta) > 0: 
                    self.fanart = self.tmdb_image + self.remotedbMeta['fanart']
            else:
                try:
                        tmdbArt = tmdbapi.getTvdb(tvdb)
                        try: 
                            tmdbArt = json.loads(tmdbArt)
                            tmdbArt = tmdbArt['tv_results'][0]
                        except: artmeta = False
                        
                        try:
                            tmdb = tmdbArt['id']
                            if tmdb == '' or tmdb == None: tmdb = '0'
                        except:
                            pass             
                        try:
                            poster2 = tmdbArt['poster_path']
                            if poster2 != '' and poster2 != '0' and poster2 != None:
                                self.poster = self.tmdb_poster + poster2
                                poster = poster
                        except:
                            pass
                        try:
                            if fanart == '0' or fanart == '' or fanart == None:
                                fanart = tmdbArt['backdrop_path']
                                self.fanart = self.tmdb_image + fanart
                        except:
                            self.fanart = '0'   
                except: pass
            if self.fanart == '' or self.fanart == '0' or self.fanart == None: self.fanart = tvdbapi.getFanart(tvdb)                    
                
                
            return self.fanart
        except:
            pass
            
    def threadSeasons(self, tvdb):
        try:
            try:self.seasons_posters = tvdbapi.getSeasonsFull(tvdb)
            except: self.seasons_posters = '0'
            return self.seasons_posters

        except:
            pass
    
    def super_info(self, i):
        try:
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'
            
            id = self.list[i]['id'] if 'id' in self.list[i] else '0'
            epnumber = self.list[i]['epnumber'] if 'epnumber' in self.list[i] else '0'
            url = self.tvdb2_get_episode % id
            result = tvdbapi.getTvdb(url)
            item = json.loads(result)
            item = item['data']
            try:thumb = item['filename']
            except: thumb = '0'
            if thumb == '': thumb = '0'
            if not thumb == '0': 
                thumb = self.tvdb_image + thumb
                self.list[i].update({'thumb': thumb})
                


            try:title = item['episodeName']
            except: title = '0'
            if title == '': title = '0'
            if not title == '0': 
                self.list[i].update({'title': title})
                self.list[i].update({'label': title})
                
            try:plot = item['overview']
            except: plot = '0'
            if plot == '': plot = '0'
            if not plot == '0': 
                self.list[i].update({'plot': plot})
                
            try:plot = item['overview']
            except: plot = '0'
            if plot == '': plot = '0'
            if not plot == '0': 
                self.list[i].update({'plot': plot})


            try:premiered = item['firstAired']
            except: premiered = '0'
            if premiered == '': premiered = '0'
            if not premiered == '0': 
                self.list[i].update({'premiered': premiered})
            
            try: rating = item.get('siteRating')
            except: rating = ''
            rating = str(rating)
            if rating == '': rating = '0'
            rating = rating
            if not rating == '0': 
                self.list[i].update({'rating': rating})
                        

            try: votes = item.get('siteRatingCount')
            except: votes = ''
            if votes == '' or votes == None: votes = '0'
            if not votes == '0': 
                self.list[i].update({'votes': votes})
                
            # BANNER OR CLEARLOGO META
            try:clearlogo = item['clearlogo']
            except: clearlogo = '0'
            if clearlogo == '': clearlogo = '0'
            try:banner = item['banner']
            except: banner = '0'
            if banner == '': banner = '0'
            
            if clearlogo == '0' or banner == '0':
                try:
                    ftvmeta = fanarttv.get(tvdb, 'tv')
                    if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                    if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']  
                except:pass         
            if not clearlogo == '0':  self.list[i].update({'clearlogo': clearlogo})
            if not banner == '0':  self.list[i].update({'banner': banner})

        except:
            pass
                
        
    def seasonDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        try: indicators = playcount.getSeasonIndicators(items[0]['imdb'])
        except: pass

        watchedMenu = control.lang(32068) if trakt.getTraktIndicatorsInfo() == True else control.lang(32066)

        unwatchedMenu = control.lang(32069) if trakt.getTraktIndicatorsInfo() == True else control.lang(32067)

        queueMenu = control.lang(32065)

        traktManagerMenu = control.lang(32070)

        labelMenu = control.lang(32055)

        playRandom = control.lang(32535)

        addToLibrary = control.lang(32551)

        for i in items:
            try:
                label = '%s %s' % (labelMenu, i['season'])
                systitle = sysname = urllib.parse.quote_plus(i['tvshowtitle'])
                
                if "tmdbMeta" in i: tmdbMeta = 'true'
                else: tmdbMeta = 'false'
                
                try: tmdb = i['tmdb']
                except: tmdb = '0'
                if tmdb != '0' and tmdb != None: tmdbMeta = 'true'
                                
                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"
                imdb, tvdb, year, season = i['imdb'], i['tvdb'], i['year'], i['season']
                meta = dict((k,v) for k, v in i.items() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tvdb_id': tvdb})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass
    
                try: meta.update({'tvshowtitle': i['label']})
                except: pass
                try: meta.update({'year': i['premiered']})
                except: pass
                
                
                sysmeta = urllib.parse.quote_plus(json.dumps(meta))
                if tmdbMeta != 'true': url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s' % (sysaddon, systitle, year, imdb, tvdb, season)
                else: url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&tmdb=%s&season=%s' % (sysaddon, systitle, year, imdb, tvdb, tmdb, season)

                cm = []             
                try:
                    if traktCredentials != True: raise Exception()
                    if season in indicators: 
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=6)' % (sysaddon, systitle, imdb, tvdb, season)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else: 
                        cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=7)' % (sysaddon, systitle, imdb, tvdb, season)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                try:
                    if traktCredentials == True: raise Exception()
                    cm.append(('Mark Season as Watched', 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=7)' % (sysaddon, systitle, imdb, tvdb, season)))

                    cm.append(('Mark Season as Unwatched', 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=6)' % (sysaddon, systitle, imdb, tvdb, season)))

                except:
                    pass

                    
                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=episode&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s)' % (sysaddon, urllib.parse.quote_plus(systitle), urllib.parse.quote_plus(year), urllib.parse.quote_plus(imdb), urllib.parse.quote_plus(tvdb), urllib.parse.quote_plus(season))))

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))


                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (sysaddon, systitle, year, imdb, tvdb)))

                item = control.item(label=label)

                art = {}

                if 'thumb' in i and not i['thumb'] == '0':
                    art.update({'icon': i['thumb'], 'thumb': i['thumb'], 'poster': i['thumb']})
                elif 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setInfo(type='Video', infoLabels = meta)

                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        try: control.property(syshandle, 'showplot', items[0]['plot'])
        except: pass

        control.content(syshandle, 'seasons')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('seasons', {'skin.estuary': 55, 'skin.confluence': 500})


class episodes:
    def __init__(self):
        self.list = []

        self.trakt_link = 'http://api.trakt.tv'
        self.tvmaze_link = 'http://api.tvmaze.com'
        self.tvdb_key = control.setting('tvdb.api')
        if self.tvdb_key == '' or self.tvdb_key == '0' or self.tvdb_key == None: self.tvdb_key = '69F2FCC839393569'
        
        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone): self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
        else: self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))
        
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.trakt_user = control.setting('trakt.user').strip()
        self.lang = control.apiLanguage()['tvdb']
        
        self.Today = (self.datetime).strftime('%Y-%m-%d')
        self.Yesterday = (self.datetime - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
        self.lastYear = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.lastMonth = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.last60days = (self.datetime - datetime.timedelta(days = 60)).strftime('%Y-%m-%d')       
        self.trakt_sortby = int(control.setting('trakt.sortby'))

        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key, '%s', '%s')
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'

        self.added_link = 'http://api.tvmaze.com/schedule'
        self.mycalendar_link = 'http://api.trakt.tv/calendars/my/shows/%s/30/' % self.lastMonth
        self.trakthistory_link = 'http://api.trakt.tv/users/me/history/shows?limit=300'
        self.progress_link = 'http://api.trakt.tv/users/me/watched/shows'
        self.hiddenprogress_link = 'http://api.trakt.tv/users/hidden/progress_watched?limit=1000&type=show'
        self.calendar_link = 'http://api.tvmaze.com/schedule?date=%s'
        self.airingtoday_link = 'http://api.trakt.tv/users/me/watched/shows?extended=noseasons'
        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'

    def getLibrary(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, meta=None, idx=True, create_directory=True):
        try:

            self.list = seasons().tvdbLibrary(tvshowtitle, year, imdb, tvdb, self.lang)
            return self.list
        except:
            pass

    def getTMDB(self, tvshowtitle, year, imdb, tvdb, tmdb, season=None, create_directory = True):
        try:
            #print ("GET TMDB")
            #print (tvshowtitle)
            self.list = cache.get(seasons().tmdb_list, 24, tvshowtitle, year, imdb, tvdb, tmdb, season, None, 'episodes')
            action = 'episodes'
            if create_directory == True: self.episodeDirectory(self.list, action=action)
            else: return self.list
        except:
            pass
            
    def tvtime(self, results):
        self.episodes = []
        for item in results:
            epName = item['name']
            show = item['show']
            tvshowtitle = show['name']
            epId = item['id']
            tvdb = show['id']
            epNum = item['number']
            snNum = item['season_number']
            data = self.get(tvshowtitle, '0', '0', tvdb, tvdb_epId = epId)

            
    def get(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, meta=None, idx=True, tvdb_epId=None, create_directory=True):
        try:
            if tvdb_epId != None: # GET EPISODE INFO BASED ON TVDB ID
                self.list = cache.get(seasons().tmdb_list, 24, tvshowtitle, year, imdb, tvdb, self.lang, None, None, tvdb_epId, 'episode_info')
                action = 'episodes'         
            elif idx == True:
                if season == None and episode == None:
                    self.list = cache.get(seasons().tvdb_list, 24, tvshowtitle, year, imdb, tvdb, self.lang, None, None, None, 'full')
                    action = 'episodes'
                elif episode == None:
                    self.list = cache.get(seasons().tvdb_list, 24, tvshowtitle, year, imdb, tvdb, self.lang, season, None, None, 'episodes')
                    action = 'episodes'
                else:
                    self.list = cache.get(seasons().tvdb_list, 24, tvshowtitle, year, imdb, tvdb, self.lang, None, None, None, 'full')
                    num = [x for x,y in enumerate(self.list) if y['season'] == str(season) and  y['episode'] == str(episode)][-1]
                    self.list = [y for x,y in enumerate(self.list) if x >= num]
                    action = 'episodes'

                if create_directory == True: self.episodeDirectory(self.list, action=action)
                return self.list
            else:
                self.list = cache.get(seasons().tvdb_list, 24, tvshowtitle, year, imdb, tvdb, 'en', None, None, None, 'full')
                return self.list
        except:pass



    def calendar(self, url):

        try:
            try: url = getattr(self, url + '_link')
            except: pass
            tvshowlabel = False

            action = ''
            if self.trakt_link in url and url == self.progress_link:
                self.blist = cache.get(self.trakt_progress_list, 720, url, self.trakt_user, self.lang)
                self.list = []
                self.list = cache.get(self.trakt_progress_list, 0, url, self.trakt_user, self.lang)
                
                #self.list = sorted(self.list, key=lambda x: x['last_watched_at'])
                
                action = 'episodes'
                tvshowlabel = True

            elif self.trakt_link in url and url == self.mycalendar_link:
                self.blist = cache.get(self.trakt_episodes_list, 720, url, self.trakt_user, self.lang)
                self.list = []
                self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)
                action = 'episodes'
                tvshowlabel = True
                
            elif self.trakt_link in url and '/users/' in url:
                self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)
                self.list = self.list[::-1]
                tvshowlabel = True              

            elif self.trakt_link in url:
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                action = 'episodes'
                
            elif self.tvmaze_link in url and url == self.added_link:
                urls = [i['url'] for i in self.calendars(idx=False)][:5]
                self.list = []
                for url in urls:
                    self.list += cache.get(self.tvmaze_list, 720, url, True)

            elif self.tvmaze_link in url:
                self.list = cache.get(self.tvmaze_list, 1, url, False)


            self.episodeDirectory(self.list, action=action, tvshowlabel=tvshowlabel)
            return self.list
        except:
            pass


    def widget(self):
        if trakt.getTraktIndicatorsInfo() == True:
            setting = control.setting('tv.widget.alt')
        else:
            setting = control.setting('tv.widget')

        if setting == '2':
            self.calendar(self.progress_link)
        elif setting == '3':
            self.calendar(self.mycalendar_link)
        else:
            self.calendar(self.added_link)


    def calendars(self, idx=True):
        m = control.lang(32060).split('|')
        try: months = [(m[0], 'January'), (m[1], 'February'), (m[2], 'March'), (m[3], 'April'), (m[4], 'May'), (m[5], 'June'), (m[6], 'July'), (m[7], 'August'), (m[8], 'September'), (m[9], 'October'), (m[10], 'November'), (m[11], 'December')]
        except: months = []

        d = control.lang(32061).split('|')
        try: days = [(d[0], 'Monday'), (d[1], 'Tuesday'), (d[2], 'Wednesday'), (d[3], 'Thursday'), (d[4], 'Friday'), (d[5], 'Saturday'), (d[6], 'Sunday')]
        except: days = []

        for i in range(0, 30):
            try:
                name = (self.datetime - datetime.timedelta(days = i))
                name = (control.lang(32062) % (name.strftime('%A'), name.strftime('%d %B')))
                for m in months: name = name.replace(m[1], m[0])
                for d in days: name = name.replace(d[1], d[0])
                try: name = name
                except: pass

                url = self.calendar_link % (self.datetime - datetime.timedelta(days = i)).strftime('%Y-%m-%d')

                self.list.append({'name': name, 'url': url, 'image': 'calendar.png', 'action': 'calendar'})
            except:
                pass
        if idx == True: self.addDirectory(self.list)
        return self.list


    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            activity = trakt.getActivity()
        except:
            pass

        try:
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
        except:
            pass
        try:
            self.list = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlikedlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'calendar'})
        self.addDirectory(self.list, queue=True)
        return self.list


    def trakt_list(self, url, user):
        try:
            # for i in re.findall('date\[(\d+)\]', url):
                # url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.parse.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urllib.parse.urlparse(url).query, '') + '?' + q

            itemlist = []
            items = trakt.getTraktAsJson(u)
        except:
            return

        for item in items:
            try:
                title = item['episode']['title']
                if title == None or title == '': raise Exception()
                title = client.replaceHTMLCodes(title)

                season = item['episode']['season']
                season = re.sub('[^0-9]', '', '%01d' % int(season))
                if season == '0': raise Exception()

                episode = item['episode']['number']
                episode = re.sub('[^0-9]', '', '%01d' % int(episode))
                if episode == '0': raise Exception()

                tvshowtitle = item['show']['title']
                if tvshowtitle == None or tvshowtitle == '': raise Exception()
                tvshowtitle = client.replaceHTMLCodes(tvshowtitle)

                year = item['show']['year']
                year = re.sub('[^0-9]', '', str(year))

                imdb = item['show']['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                tvdb = item['show']['ids']['tvdb']
                if tvdb == None or tvdb == '': raise Exception()
                tvdb = re.sub('[^0-9]', '', str(tvdb))

                premiered = item['episode']['first_aired']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'

                studio = item['show']['network']
                if studio == None: studio = '0'

                genre = item['show']['genres']
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)

                try: duration = str(item['show']['runtime'])
                except: duration = '0'
                if duration == None: duration = '0'

                try: rating = str(item['episode']['rating'])
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'

                try: votes = str(item['show']['votes'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None: votes = '0'

                mpaa = item['show']['certification']
                if mpaa == None: mpaa = '0'

                plot = item['episode']['overview']
                if plot == None or plot == '': plot = item['show']['overview']
                if plot == None or plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)

                try:
                    if self.lang == 'en': raise Exception()

                    item = trakt.getTVShowTranslation(imdb, lang=self.lang, season=season, episode=episode,  full=True)

                    title = item.get('title') or title
                    plot = item.get('overview') or plot

                    tvshowtitle = trakt.getTVShowTranslation(imdb, lang=self.lang) or tvshowtitle
                except:
                    pass

                itemlist.append({'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': 'Continuing', 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'thumb': '0'})
            except:
                pass

        itemlist = itemlist[::-1]

        return itemlist


    def trakt_progress_list(self, url, user, lang):
        try:
            url += '?extended=full'
            result = trakt.getTraktAsJson(url)

            items = []
        except:
            return

        for item in result:
            try:
                num_1 = 0
                for i in range(0, len(item['seasons'])):
                    if item['seasons'][i]['number'] > 0: num_1 += len(item['seasons'][i]['episodes'])
                num_2 = int(item['show']['aired_episodes'])
                if num_1 >= num_2: raise Exception()

                season = str(item['seasons'][-1]['number'])

                episode = [x for x in item['seasons'][-1]['episodes'] if 'number' in x]
                episode = sorted(episode, key=lambda x: x['number'])
                episode = str(episode[-1]['number'])

                tvshowtitle = item['show']['title']
                if tvshowtitle == None or tvshowtitle == '': raise Exception()
                tvshowtitle = client.replaceHTMLCodes(tvshowtitle)

                year = item['show']['year']
                year = re.sub('[^0-9]', '', str(year))
                if int(year) > int(self.datetime.strftime('%Y')): raise Exception()

                imdb = item['show']['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'

                tvdb = item['show']['ids']['tvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))

                tmdb = item['show']['ids']['tmdb']
                if tmdb == None or tmdb == '': raise Exception()
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                
                watched_at = item['last_watched_at']
                
                items.append({'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season, 'enum': episode, 'last_watched_at': watched_at})
            except:
                pass

        try:
            result = trakt.getTraktAsJson(self.hiddenprogress_link)
            result = [str(i['show']['ids']['tmdb']) for i in result]

            items = [i for i in items if not i['tmdb'] in result]
        except:
            pass

        def items_list(i):
            try:
                nextEp = int(i['enum']) + 1
                nextSs = int(i['snum']) + 1
                itemList = []

                try:itemList = [x for x in self.blist if x['tmdb'] == i['tmdb'] and x['season'] == i['snum'] and x['episode'] == str(nextEp)][0]
                except:pass
                try: itemList = [x for x in self.blist if x['tmdb'] == i['tmdb'] and x['season'] == str(nextSs) and x['episode'] == '1'][0]
                except:pass
                item  = itemList
                if not 'tvshowtitle' in item and len(item) < 1: raise Exception()
                item['action'] = 'episodes'
                item['last_watched_at'] = i['last_watched_at']          
                self.list.append(item)
                return
            except:
                pass
                    # def tvdb_list(self, tvshowtitle, year, imdb, tvdb, lang, season=None, episode=None, tvdb_epId = None, limit='seasons'):
            try:
                tmdbList = cache.get(seasons().tmdb_list, 24, i['tvshowtitle'], i['year'], i['imdb'], i['tvdb'], i['tmdb'], i['snum'],  i['enum'], 'nextepisode')
                item = tmdbList[0]
                item['action'] = 'episodes'
                item['last_watched_at'] = i['last_watched_at']                  
                self.list.append(item)

                return
            except:
                pass


        items = items[:100]
        
        threads = []
        for i in items: threads.append(libThread.Thread(items_list, i))
        [i.start() for i in threads]
        [i.join() for i in threads]

        
        try: self.list = sorted(self.list, key=lambda x: x['last_watched_at'], reverse=True)
        except: pass
        
        if self.trakt_sortby == 1:
            try: self.list = sorted(self.list, key=lambda k: k['premiered'], reverse=True)
            except: pass
        elif self.trakt_sortby == 2: 
            try: self.list = sorted(self.list, key=lambda k: utils.title_key(k['tvshowtitle']))
            except: pass
            
        return self.list

    def trakt_airing_today(self):
        try:
            result = trakt.getTraktAsJson(self.airingtoday_link)
            items = []
        except:
            return
        try:
            for item in result:
                try:

                    tvshowtitle = item['show']['title']
                    if tvshowtitle == None or tvshowtitle == '': raise Exception()
                    tvshowtitle = client.replaceHTMLCodes(tvshowtitle)

                    year = item['show']['year']
                    year = re.sub('[^0-9]', '', str(year))
                    if int(year) > int(self.datetime.strftime('%Y')): raise Exception()

                    imdb = item['show']['ids']['imdb']
                    if imdb == None or imdb == '': imdb = '0'

                    tvdb = item['show']['ids']['tvdb']
                    if tvdb == None or tvdb == '': raise Exception()
                    tvdb = re.sub('[^0-9]', '', str(tvdb))

                    items.append({'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year})
                except:
                    pass
                    
            try:
                result = trakt.getTraktAsJson(self.hiddenprogress_link)
                result = [str(i['show']['ids']['tvdb']) for i in result]
                items = [i for i in items if not i['tvdb'] in result]
            except:
                pass
                
            
        except:pass
        return items            
            
    def trakt_episodes_list(self, url, user, lang):
        items = self.trakt_list(url, user)
        def items_list(i):
            try:
                item = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['season'] == i['season'] and x['episode'] == i['episode']][0]
                if item['poster'] == '0': raise Exception()
                item['action'] = 'episodes'
                self.list.append(item)
                return
            except:
                pass

            try:
                tvdbList = cache.get(seasons().tvdb_list, 24, i['tvshowtitle'], i['year'], i['imdb'], i['tvdb'], self.lang, i['season'],  i['episode'], None, 'episode_info')
                item = tvdbList[0]
                item['action'] = 'episodes'
                self.list.append(item)
                #print(self.list)
                return
            except:
                pass

        items = items[:100]
        
        threads = []
        for i in items: threads.append(libThread.Thread(items_list, i))
        [i.start() for i in threads]
        [i.join() for i in threads]

        try: self.list = sorted(self.list, key=lambda k: k['premiered'], reverse=True)
        except: pass        

        return self.list


    def trakt_user_list(self, url, user):
        try:
            items = trakt.getTraktAsJson(url)
        except:
            pass

        for item in items:
            try:
                try: name = item['list']['name']
                except: name = item['name']
                name = client.replaceHTMLCodes(name)

                try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except: url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

                self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list


    def tvmaze_list(self, url, limit):
        try:
            result = client.request(url)

            itemlist = []
            items = json.loads(result)
        except:
            return

        for item in items:
            try:
                if not 'english' in item['show']['language'].lower(): raise Exception()

                if limit == True and not 'scripted' in item['show']['type'].lower(): raise Exception()

                title = item['name']
                if title == None or title == '': raise Exception()
                title = client.replaceHTMLCodes(title)
                title = title

                season = item['season']
                season = re.sub('[^0-9]', '', '%01d' % int(season))
                if season == '0': raise Exception()
                season = season

                episode = item['number']
                episode = re.sub('[^0-9]', '', '%01d' % int(episode))
                if episode == '0': raise Exception()
                episode = episode

                tvshowtitle = item['show']['name']
                if tvshowtitle == None or tvshowtitle == '': raise Exception()
                tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
                tvshowtitle = tvshowtitle

                year = item['show']['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year

                imdb = item['show']['externals']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb

                tvdb = item['show']['externals']['thetvdb']
                if tvdb == None or tvdb == '': raise Exception()
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb

                poster = '0'
                try: poster = item['show']['image']['original']
                except: poster = '0'
                if poster == None or poster == '': poster = '0'
                poster = poster

                try: thumb1 = item['show']['image']['original']
                except: thumb1 = '0'
                try: thumb2 = item['image']['original']
                except: thumb2 = '0'
                if thumb2 == None or thumb2 == '0': thumb = thumb1
                else: thumb = thumb2
                if thumb == None or thumb == '': thumb = '0'
                thumb = thumb

                premiered = item['airdate']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered

                try: studio = item['show']['network']['name']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio

                try: genre = item['show']['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre

                try: duration = item['show']['runtime']
                except: duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration

                try: rating = item['show']['rating']['average']
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating

                try: plot = item['show']['summary']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                plot = client.replaceHTMLCodes(plot)
                plot = plot

                itemlist.append({'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': 'Continuing', 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'thumb': thumb})
            except:
                pass

        itemlist = itemlist[::-1]

        return itemlist
        
        
    def inProgress(self):
        try:
            if control.setting('inprogress.tv.type') == '1':
                from resources.lib.api import remotedb
                type = 'tv'
                remotedb.getInProgress(type)
                raise Exception()
                
            if control.setting('inprogress.tv.type') == '2':
                self.calendar(self.progress_link)
                raise Exception()
            #print ("IN PROGRESS EPISODES")              
            from resources.lib.modules import favourites
            items = favourites.getProgress('tv')
            self.list = [i[1] for i in items]
            #print(("IN PROGRESS EPISODES", self.list))

        

            # self.worker()
            
            self.inProgressDir(self.list)
        except:
            return          
        
        
    def inProgressDir(self, items, tvshowlabel=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()
        #print ("IN PROGRESS ITEMS")
        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getTVShowIndicators(refresh=True)
        
        tvshowlabel = tvshowlabel

        try: sysaction = items[0]['action']
        except: sysaction = ''
        
        if sysaction == '' or sysaction == None: sysaction = action
        
        isFolder = False

        playbackMenu = control.lang(32063) if control.setting('hosts.mode') == '2' or control.setting('hosts.mode') == '3' else control.lang(32064)

        watchedMenu = control.lang(32068) if trakt.getTraktIndicatorsInfo() == True else control.lang(32066)

        unwatchedMenu = control.lang(32069) if trakt.getTraktIndicatorsInfo() == True else control.lang(32067)

        queueMenu = control.lang(32065)

        traktManagerMenu = control.lang(32070)

        tvshowBrowserMenu = control.lang(32071)

        addToLibrary = control.lang(32551)

        for i in items:
            #print(("IN PROGRESS ITEMS", i))
            try:
                if not 'label' in i: i['label'] = i['title']

                if i['label'] == '0':
                    label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                else:
                    label = 'S%s:E%s - %s' % (i['season'], i['episode'], i['label'])
                    systitle = urllib.parse.quote_plus(i['title'])
                    
                if 'tvshowtitle' in i: label = '%s - %s' % (i['tvshowtitle'], label)
                    
                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): 
                    label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"
                    i['thumb'] = control.addonFanart()

                imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                
                systvshowtitle = urllib.parse.quote_plus(i['tvshowtitle'])
                syspremiered = urllib.parse.quote_plus(i['premiered'])

                if "tmdbMeta" in i: tmdbMeta = 'true'
                else: tmdbMeta = 'false'
                
                try: tmdb = i['tmdb']
                except: tmdb = '0'
                if tmdb != '0' and tmdb != None: tmdbMeta = 'true'
                
                meta = dict((k,v) for k, v in i.items() if v != '0' and v != 'None')
                meta.update({'mediatype': 'episode'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, systvshowtitle)})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                # try: meta.update({'duration': str(int(meta['duration']) * 60)})
                # except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass
                try: meta.update({'year': re.findall('(\d{4})', i['premiered'])[0]})
                except: pass
                try: meta.update({'title': i['label']})
                except: pass

                sysmeta = urllib.parse.quote_plus(json.dumps(meta))


                if tmdbMeta != 'true': url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)
                else: url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&tmdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, tmdb, season, episode, systvshowtitle, syspremiered, sysmeta)

                sysurl = urllib.parse.quote_plus(url)


                if isFolder == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season, episode)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                if tvshowlabel == True:
                    cm.append((tvshowBrowserMenu, 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))

                try:
                    overlay = int(playcount.getEpisodeOverlay(indicators, season, episode, imdb=imdb, tvdb=tvdb, tmdb=tmdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&tmdb=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode, tmdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&tmdb=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode, tmdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, systvshowtitle, tvdb)))

                if isFolder == False:
                    cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                if isOld == True:
                    cm.append((control.lang2(19033), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))
                # cm.append(('Play With Exodus', 'RunPlugin(plugin://plugin.video.exodus/?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&t=%s)' % (systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta, self.systime)))

                item = control.item(label=label)

                art = {}

                if 'poster' in i and not i['poster'] == '0':
                    art.update({'poster': i['poster'], 'tvshow.poster': i['poster'], 'season.poster': i['poster']})
                else:
                    art.update({'poster': addonPoster})

                if 'thumb' in i and not i['thumb'] == '0':
                    art.update({'icon': i['thumb'], 'thumb': i['thumb']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'icon': i['fanart'], 'thumb': i['fanart']})
                elif 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster']})
                else:
                    art.update({'icon': addonFanart, 'thumb': addonFanart})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})
                    
                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                #item.setProperty('IsPlayable', isPlayable)
                
                # played = bookmarks.bookmarks().get(bookmarkname)
                # item.setProperty('resumetime', played)
                
                item.setInfo(type='Video', infoLabels = meta)

                # video_streaminfo = {'codec': 'h264'}
                # item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except:
                pass

        control.content(syshandle, 'episodes')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('episodes', {'skin.estuary': 55, 'skin.confluence': 504})


        
        


    def episodeDirectory(self, items, action='', tvshowlabel=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getTVShowIndicators(refresh=True)
        
        tvshowlabel = tvshowlabel

        try: sysaction = items[0]['action']
        except: sysaction = ''
        
        if sysaction == '' or sysaction == None: sysaction = action
        
        isFolder = False if sysaction == 'episodes' else True

        playbackMenu = control.lang(32063) if control.setting('hosts.mode') == '2' or control.setting('hosts.mode') == '3' else control.lang(32064)

        watchedMenu = control.lang(32068) if trakt.getTraktIndicatorsInfo() == True else control.lang(32066)

        unwatchedMenu = control.lang(32069) if trakt.getTraktIndicatorsInfo() == True else control.lang(32067)

        queueMenu = control.lang(32065)

        traktManagerMenu = control.lang(32070)

        tvshowBrowserMenu = control.lang(32071)

        addToLibrary = control.lang(32551)

        for i in items:

            try:
                if not 'label' in i: i['label'] = i['title']

                if i['label'] == '0':
                    label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                else:
                    label = 'S%s:E%s - %s' % (i['season'], i['episode'], i['label'])
                if tvshowlabel == True:
                    label = '%s - %s' % (i['tvshowtitle'], label)
                    
                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): 
                    label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"
                    i['thumb'] = control.addonFanart()

                imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                systitle = urllib.parse.quote_plus(i['title'])
                systvshowtitle = urllib.parse.quote_plus(i['tvshowtitle'])
                syspremiered = urllib.parse.quote_plus(i['premiered'])

                if "tmdbMeta" in i: tmdbMeta = 'true'
                else: tmdbMeta = 'false'
                
                try: tmdb = i['tmdb']
                except: tmdb = '0'
                if tmdb != '0' and tmdb != None: tmdbMeta = 'true'
                
                meta = dict((k,v) for k, v in i.items() if not v == '0')
                meta.update({'mediatype': 'episode'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, systvshowtitle)})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass
                try: meta.update({'year': re.findall('(\d{4})', i['premiered'])[0]})
                except: pass
                try: meta.update({'title': i['label']})
                except: pass

                sysmeta = urllib.parse.quote_plus(json.dumps(meta))


                if tmdbMeta != 'true': url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)
                else: url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&tmdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, tmdb, season, episode, systvshowtitle, syspremiered, sysmeta)

                sysurl = urllib.parse.quote_plus(url)


                if isFolder == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season, episode)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                if tvshowlabel == True:
                    cm.append((tvshowBrowserMenu, 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))

                try:
                    overlay = int(playcount.getEpisodeOverlay(indicators, season, episode, imdb=imdb, tvdb=tvdb, tmdb=tmdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&tmdb=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode, tmdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&tmdb=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode, tmdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, systvshowtitle, tvdb)))

                if isFolder == False:
                    cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                if isOld == True:
                    cm.append((control.lang2(19033), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))
                # cm.append(('Play With Exodus', 'RunPlugin(plugin://plugin.video.exodus/?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&t=%s)' % (systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta, self.systime)))

                item = control.item(label=label)

                art = {}

                if 'poster' in i and not i['poster'] == '0':
                    art.update({'poster': i['poster'], 'tvshow.poster': i['poster'], 'season.poster': i['poster']})
                else:
                    art.update({'poster': addonPoster})

                if 'thumb' in i and not i['thumb'] == '0':
                    art.update({'icon': i['thumb'], 'thumb': i['thumb']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'icon': i['fanart'], 'thumb': i['fanart']})
                elif 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster']})
                else:
                    art.update({'icon': addonFanart, 'thumb': addonFanart})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})
                    
                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                #item.setProperty('IsPlayable', isPlayable)
                
                # played = bookmarks.bookmarks().get(bookmarkname)
                # item.setProperty('resumetime', played)
                
                item.setInfo(type='Video', infoLabels = meta)

                # video_streaminfo = {'codec': 'h264'}
                # item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except:
                pass

        control.content(syshandle, 'episodes')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('episodes', {'skin.estuary': 55, 'skin.confluence': 504})


    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065)

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.parse.quote_plus(i['url'])
                except: pass

                cm = []

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


