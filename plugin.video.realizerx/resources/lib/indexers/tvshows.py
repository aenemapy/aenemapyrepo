# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

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
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import views
from resources.lib.modules import utils
from resources.lib.api import tvdbapi, tmdbapi, fanarttv
from resources.lib.modules import favourites
import os,sys,re,json,urllib.request,urllib.parse,urllib.error,urllib.parse,datetime
from resources.lib.modules import metalibrary
import libThread
from resources.lib.modules.lib_titles import cleantitle_get, normalize_string

import requests
from bs4 import BeautifulSoup
params = dict(urllib.parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

import requests


class tvshows:
    def __init__(self):
        self.list = []
        self.remotedbMeta = []
        self.limit = False
        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api.trakt.tv'
        self.tvmaze_link = 'http://www.tvmaze.com'
        self.tmdb_link = 'https://api.themoviedb.org'
        
        self.tvdb_key = control.setting('tvdb.api')
        if self.tvdb_key == '' or self.tvdb_key == '0' or self.tvdb_key == None: self.tvdb_key = '69F2FCC839393569'
        
        self.sortby = 'list_order,asc'
        if control.setting('imdb.sortlist') == '0'  : self.sortby = 'list_order,asc'
        elif control.setting('imdb.sortlist') == '1': self.sortby = 'moviemeter,asc'
        elif control.setting('imdb.sortlist') == '2': self.sortby = 'user_rating,desc'
        elif control.setting('imdb.sortlist') == '3': self.sortby = 'alpha,asc'
            
        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone): self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
        else: self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))
        
        
        self.Today = (self.datetime).strftime('%Y-%m-%d')
        self.Yesterday = (self.datetime - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
        self.lastYear = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.lastMonth = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.last60days = (self.datetime - datetime.timedelta(days = 60)).strftime('%Y-%m-%d')
        
        
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        
        
        self.user = 'solaris'
        self.lang = control.apiLanguage()['tvdb']
        # self.posterProvider = 'IMDB'
        # if int(control.setting('poster.provider.tv') == 1: self.posterProvider = 'TMDB'
        # elif int(control.setting('poster.provider.tv') == 2: self.posterProvider = 'TVDB'
        
        self.search_link = 'http://api.trakt.tv/search/show?limit=20&page=1&query='
        self.tvmaze_info_link = 'http://api.tvmaze.com/shows/%s'
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key, '%s', self.lang)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'

        poster_size = ['w154', 'w500', 'original']
        fanart_size = ['w300', 'w1280', 'original']
        
        poster_quality = poster_size[int(control.setting('poster.type'))]
        fanart_quality = fanart_size[int(control.setting('fanart.type'))]
        
        self.tmdb_image = 'https://image.tmdb.org/t/p/%s'  % fanart_quality
        self.tmdb_poster = 'https://image.tmdb.org/t/p/%s' % poster_quality     
        
        self.persons_link = 'http://www.imdb.com/search/name?count=100&name='
        self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&sort=moviemeter,asc&count=40&start=1'
        self.airing_link = 'http://www.imdb.com/search/title?title_type=tv_episode&release_date=%s,%s&sort=moviemeter,asc&count=40&start=1' % (self.Yesterday, self.Today)
        self.active_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=10,&production_status=active&sort=moviemeter,asc&count=40&start=1'
        self.premiere_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=10,&release_date=%s,%s&sort=moviemeter,asc&count=40&start=1' % (self.lastMonth, self.Today)
        self.rating_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=5000,&release_date=,%s&sort=user_rating,desc&count=40&start=1' % (self.Today)
        self.views_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&release_date=,%s&sort=num_votes,desc&count=40&start=1' % (self.Today)
        self.person_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,%s&role=%s&sort=year,desc&count=40&start=1' % (self.Today, "%s")
        self.genre_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,%s&genres=%s&sort=moviemeter,asc&count=40&start=1' % (self.Today, "%s")
        self.keyword_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,%s&keywords=%s&sort=moviemeter,asc&count=40&start=1' % (self.Today, "%s")
        self.language_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&production_status=released&primary_language=%s&sort=moviemeter,asc&count=40&start=1'
        self.certification_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,%s&certificates=us:%s&sort=moviemeter,asc&count=40&start=1' % (self.Today, "%s")
        self.trending_link = 'http://api.trakt.tv/shows/trending?limit=40&page=1'
        self.emmy_link = 'http://www.imdb.com/search/title?groups=emmy_winners&title_type=tv_series,mini_series&start=1'
                
        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api.trakt.tv/users/me/collection/shows'
        self.traktwatchlist_link = 'http://api.trakt.tv/users/me/watchlist/shows'
        self.traktfeatured_link = 'http://api.trakt.tv/recommendations/shows?limit=40'
        self.traktrecommended_link = 'http://api.trakt.tv/recommendations/shows?limit=100'
        
        ############# IMDB LISTS ###################
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&title_type=tvSeries,tvMiniSeries&start=1&sort=%s&st_dt=&mode=detail&page=1' % ("%s", self.sortby)
        # list 2 USED TO HARDCODE SORT ORDER i.e. Watchlist
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&title_type=tvSeries,tvMiniSeries&start=1&sort=%s&st_dt=&mode=detail&page=1' % ("%s", "%s")
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=%s&title_type=tvSeries,tvMiniSeriess&mode=detail&page=1'  % (self.imdb_user, self.sortby)
        
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

        # TMDB LISTS
        ############################################
        self.tmdbupcoming_link = 'https://api.themoviedb.org/3/tv/upcoming?api_key=%s&language=en-US&page=1'                
        self.tmdbtoprated_link = 'https://api.themoviedb.org/3/tv/top_rated?api_key=%s&language=en-US&page=1'       
        self.tmdbpopular_link = 'https://api.themoviedb.org/3/tv/popular?api_key=%s&language=en-US&page=1'
        self.tmdbairingtoday_link = 'https://api.themoviedb.org/3/tv/airing_today?api_key=%s&language=en-US&page=1' 
        self.tmdbtrending_link = 'https://api.themoviedb.org/3/trending/tv/day?api_key=%s&page=1'
        self.tmdbperson = 'https://api.themoviedb.org/3/person/%s/tv_credits?api_key=%s&language=en-US'     
        self.tmdbperson_search = 'https://api.themoviedb.org/3/search/person?api_key=%s&language=en-US&query=%s&page=1&include_adult=false'
        self.tmdbgenres ='https://api.themoviedb.org/3/discover/tv?api_key=%s&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&with_genres=%s&page=1'     
        self.tmdbfavourites_link = 'https://api.themoviedb.org/3/account/%s/favorite/tv?api_key=%s&session_id=%s&language=en-US&sort_by=created_at.desc&page=1'
        self.tmdbwatchlist_link  = 'https://api.themoviedb.org/3/account/%s/watchlist/tv?api_key=%s&language=en-US&session_id=%s&sort_by=created_at.desc&page=1'
        self.tmdbuserlist_link   = 'https://api.themoviedb.org/3/list/%s?api_key=%s&language=en-US&page=1'
        
    def getSearch(self, title = None):
        try:
            if (title == None or title == ''): return
            url = 'https://api.thetvdb.com/search/series?name=%s'  % (urllib.parse.quote_plus(title))
            self.list = cache.get(self.getTvdb, 720, url, False)
            self.list = [i for i in self.list if cleantitle_get(title) == cleantitle.get(i['tvshowtitle'])]
            return self.list
        except:
            return  
            
    def getSearchTMDB(self, title = None, year = None):
        try:
            if (title == None or title == ''): return
            if year != None: years = [str(year), str(int(year)+1), str(int(year)-1)]
            query = cleantitle.query(title)
            url = 'https://api.themoviedb.org/3/search/tv?api_key=%s&language=en-US&query=%s&page=1' % ("%s", query)
            self.list = cache.get(self.tmdb_list, 720, url)
            self.list = [i for i in self.list if cleantitle.get(title.lower()) == cleantitle.get(i['title'].lower())]            
            if year != None: self.list = [i for i in self.list if str(i['year']) in years]
            self.workerTMDB()
            if len(self.list) > 0: return self.list

        except: pass
        
    def getSearchTVDB(self, title = None, year = None):
        try:
            if (title == None or title == ''): return
            if year != None: years = [str(year), str(int(year)+1), str(int(year)-1)]
            query = cleantitle.query(title)

            url = '%s/search/series?name=%s'  % (self.tvdb2_api, urllib.parse.quote_plus(query))
            self.list = cache.get(self.getTvdb, 720, url, False)
            self.list = [i for i in self.list if cleantitle.get(title.lower()) == cleantitle.get(i['title'].lower())]

            if year != None: self.list = [i for i in self.list if str(i['year']) in years]
            if len(self.list) > 0: return self.list
            trakt_search = trakt.SearchTVShow(query, None, False)
            traktItems = []
            for i in trakt_search:
                try: traktItems.append(i['show'])
                except: pass
            if len(traktItems) > 0: 
                self.list = []
                traktItems = [i for i in traktItems if cleantitle.get(title.lower()) == cleantitle.get(i['title'].lower())]
                if year: traktItems = [i for i in traktItems if str(i['year']) in years]
                tvdbID     = traktItems['ids']['tvdb']
                url_2      = '%s/series/%s' % (self.tvdb2_api, str(tvdbID))
                self.list  = cache.get(self.getTvdb, 720, url_2, False)
                if len(self.list) > 0: return self.list
                return
        except:
            return  

    def newTvSearch(self, title=None):
        try:
            if title == None:
                t = control.lang(32010).encode('utf-8')
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return
            
            try: 
                cacheID  = 'tv-searchdb'
                searchDB = cache.get_from_string(cacheID, 720, None)
            except: searchDB = []

            if searchDB == None: searchDB = []

            try:
                searchDB = [i for i in searchDB if not i['query'] == title][:19]
                query = {'query' : title}
                searchDB.append(query)
            except:pass
            
            r = cache.get_from_string(cacheID, 720, searchDB, update=True)
            
            self.searchTMDB(title=title)
               

        except:
            pass            
            
    def tvSearch(self):
        try:
            artPath = control.artPath()
            icon = os.path.join(artPath, 'search.png')
            syshandle = int(sys.argv[1])
            url = '%s?action=newTvSearch' % (sys.argv[0])
            item = control.item(label='NEW SEARCH >>>') 
            item.setArt({'icon': icon, 'thumb': icon})
            item.setProperty('Fanart_Image', control.addonFanart())
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            
            try: 
                cacheID  = 'tv-searchdb'
                searchDB = cache.get_from_string(cacheID, 720, None)
                searchDB.reverse()
            except: searchDB = []

            if searchDB == None: searchDB = []
            for x in searchDB:
                try:
                    query = x['query']
                    url = '%s?action=newTvSearch&title=%s' % (sys.argv[0], urllib.parse.quote_plus(query))
                    item = control.item(label=query)    
                    control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
                except: pass

            control.content(syshandle, 'files') 
            control.directory(syshandle, cacheToDisc=True)          

        except:
            pass
            
    def get(self, url, idx=True, create_directory=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urllib.parse.urlparse(url).netloc.lower()
            except: pass


            if u in self.trakt_link and '/users/' in url:
                try:
                    if not '/users/me/' in url: raise Exception()
                    if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
                except:
                    self.list = self.trakt_list(url, self.trakt_user)

                if '/users/me/' in url and '/collection/' in url:
                    self.list = sorted(self.list, key=lambda k: utils.title_key(k['title']))

                if idx == True: self.worker()

            elif u in self.trakt_link and self.search_link in url:
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                if idx == True: self.worker(level=0)

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()


            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                if '/user/' in url: self.list = cache.get(self.imdb_userlist, 24, url)
                else: self.list = cache.get(self.imdb_userlist, 720, url)
                if idx == True: self.worker(limit=True)

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                
                #self.list = self.imdb_list(url)
                if idx == True: self.worker()

            elif u in self.tmdb_link:
                if "/person/" in url: self.list = self.tmdb_person_list(url)
                else: 
                    cacheTime = 24
                    if "/account/" in url: cacheTime = 0
                    if "/list/" in url: cacheTime = 0
                    self.list = cache.get(self.tmdb_list, cacheTime, url)
                if idx == True: self.workerTMDB()
                
            elif u in self.tvmaze_link:
                self.list = cache.get(self.tvmaze_list, 168, url)
                if idx == True: self.worker()


            if idx == True and create_directory == True: self.tvshowDirectory(self.list)
            return self.list
        except:
            pass
            
            
    def imdb_request(self, url):
        headers = {'Accept-Language':'en'}
        try:r = requests.get(url, headers=headers, timeout=30).content
        except requests.Timeout as err: control.infoDialog('IMDB is Slow or Down, Please Try Later...')
        return r    
        
    def remotedb_meta(self, imdb=None, tmdb=None, tvdb=None):
        try:
            if control.setting('local.meta') != 'true': return None
            dbmeta = metalibrary.metaTV(imdb=imdb, tmdb=tmdb, tvdb=tvdb)
            return dbmeta
            
        except:pass
        
    def remotedb_addmeta(self, type, meta):
        try:
            from resources.lib.api import remotedb
            dbm = remotedb.add_metadata(type, meta)
        except:pass
            
    def getTvdbFav(self, idx=True, create_directory=True):  
        url = '0'
        if control.setting('tvdb.cache') == 'true': self.list = cache.get(self.getTvdbList, 60, url, self.user) 
        else: self.list = cself.getTvdbList(url, self.user)         
        try:self.worker()
        except:pass
        self.list = sorted(self.list, key=lambda k: utils.title_key(k['title']))
        self.tvshowDirectory(self.list) 

    def getTvdbList(self, url, user):
        self.list = []
        try:
            # #print ("TVDB MY FAV")
            ids =  tvdbapi.getFav()
            ids = json.loads(ids)
            favs = ids['data']['favorites']
        
            for fav in favs:
                tvdb = fav.encode('utf-8')              
                url =  self.tvdb2_info_series % tvdb
                
    
                result = tvdbapi.getTvdb(url)
                items = json.loads(result)
                item = items['data']

                try:

                        try: title = item['seriesName']
                        except: title = ''
                        if title == '': title = '0'
                        title = client.replaceHTMLCodes(title)
                        title = normalize_string(title)
                        if "series not permitted" in title.lower(): raise Exception()
                        try: year = item['firstAired'].encode('utf-8')
                        except: year = ''
                        try: year = re.compile('(\d{4})').findall(year)[0]
                        except: year = ''
                        if year == '': year = '0'
                        year = year.encode('utf-8')
                        try: premiered = item['firstAired'].encode('utf-8')
                        except: premiered = '0'
                        if premiered == '': premiered = '0'
                        premiered = client.replaceHTMLCodes(premiered)
                        premiered = premiered.encode('utf-8')
                        try: studio = item['network']
                        except: studio = ''
                        if studio == '': studio = '0'
                        studio = client.replaceHTMLCodes(studio)
                        studio = studio.encode('utf-8')

                        try: plot = item['overview']
                        except: plot = ''
                        if plot == '': plot = '0'
                        plot = plot.encode('utf-8')
                        # #print ("SEARCH TVDB plot", plot)              
                        tmdb = '0'
                        imdb = '0'
                        
                        self.list.append({'tvshowtitle': title, 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': '0', 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': '0', 'banner': '0', 'fanart': '0', 'next': ''})
                except:
                        continue

                

            return self.list
        except:
            pass    
            
    def getTvdb(self, url, idx=True):
        self.list = []
        try:
            result = tvdbapi.getTvdb(url)
            items = json.loads(result)
            items = items['data']

            for item in items:
                try:
                    try: 
                        tvdb = item['id']
                        tvdb = str(tvdb)
                    except: tvdb = ''
                    try: imdb = item['imdbId']
                    except: imdb = ''                       

                    if tvdb == '': raise Exception()                    

                    try: title = item['seriesName']
                    except: title = ''
                    if title == '': title = '0'
                    title = client.replaceHTMLCodes(title)
                    title = normalize_string(title)
                    if "series not permitted" in title.lower(): raise Exception()
                    try: year = item['firstAired'].encode('utf-8')
                    except: year = ''
                    try: year = re.compile('(\d{4})').findall(year)[0]
                    except: year = ''
                    if year == '': year = '0'
                    
                    try: premiered = item['firstAired'].encode('utf-8')
                    except: premiered = '0'
                    if premiered == '': premiered = '0'
                    premiered = client.replaceHTMLCodes(premiered)
                    premiered = premiered.encode('utf-8')
                    try: studio = item['network']
                    except: studio = ''
                    if studio == '': studio = '0'
                    studio = client.replaceHTMLCodes(studio)


                    try: plot = item['overview']
                    except: plot = ''
                    if plot == '': plot = '0'
                    plot = plot.encode('utf-8')
                
                    tmdb = '0'

                    try: imdb = item['imdbId']
                    except: imdb = '0'
                    
                    try: banner = item['banner']        
                    except: banner = '0'
                    if banner == '' or banner == None: banner = '0'
                    if banner != '0': banner = self.tvdb_image + banner                 
                    ##print ("SEARCH TVDB plot", plot)                       
                    self.list.append({'tvshowtitle': title, 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': '0', 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': '0', 'banner': banner, 'fanart': '0', 'next': ''})
                except:
                    continue

            
            try:self.worker()
            except:pass

            if idx == True: self.tvshowDirectory(self.list)
            return self.list
        except:
            pass            
            
    def tmdb_list(self, url):
        if "/account/" in url: result = tmdbapi.account().request(url)
        else:
            result = tmdbapi.tmdbRequest(url)
            result = json.loads(result)

        if "/list/" in url: items = result['items']
        else: items = result['results']

        for item in items:
            try:
                try: page = result.get('page')
                except: page = '1'
                try: totalPages = result.get('total_pages') 
                except: totalPages = '0'
    
                if page == None: page = '1'
                if totalPages == None: totalPages = '0'

                next = int(page) + 1
                try: 
                    nextPage = 'page=%s' % str(next)
                    currPage = re.findall('page=(\d+)', url)[0]

                    next = url.replace('page=%s' % currPage, nextPage)
                except: pass
                
                if int(page) >= int(totalPages) : next = '0'

                title = item['name']
                title = normalize_string(title)             
                tmdb = item.get('id')
                tmdb = str(tmdb)
                
                year = item['first_air_date']
                try:
                    year = re.compile('(\d{4})').findall(str(year))[0]
                except:
                    year = '0'
                    
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'tmdb': tmdb, 'tvdb': '0', 'next': next})
            except:
                pass
        return self.list

    def searchTMDB(self, title=None, create_directory=False):
        try:
            if title == None:
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return

            

            url = 'https://api.themoviedb.org/3/search/tv?api_key=%s&language=en-US&query=%s&page=1' % ("%s", title)
            self.get(url)
            #url = '%s?action=movies&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            #control.execute('Container.Update(%s)' % url)
        except: pass
        
    def searchTvdb(self, title=None):
        try:
            #control.idle()
            if title == None:
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return

            url = 'https://api.thetvdb.com/search/series?name=%s'  % (urllib.parse.quote_plus(title))
            self.getTvdb(url)
            #url = '%s?action=tvshowsTvdb&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            #control.execute('Container.Update(%s)' % url)
        except:
            return  
                    
    def search(self):
        try:
            #control.idle()

            t = control.lang(32010)
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = self.search_link + urllib.parse.quote_plus(q)
            self.get(url)
            #url = '%s?action=tvshowPage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            #control.execute('Container.Update(%s)' % url)
        except:
            return

    def genres(self):
        if control.setting('tv.list.type') == '0':        
            genres = [
                ('Action', 'action', True),
                ('Adventure', 'adventure', True),
                ('Animation', 'animation', True),
                ('Anime', 'anime', False),
                ('Biography', 'biography', True),
                ('Comedy', 'comedy', True),
                ('Crime', 'crime', True),
                ('Drama', 'drama', True),
                ('Family', 'family', True),
                ('Fantasy', 'fantasy', True),
                ('Game-Show', 'game_show', True),
                ('History', 'history', True),
                ('Horror', 'horror', True),
                ('Music ', 'music', True),
                ('Musical', 'musical', True),
                ('Mystery', 'mystery', True),
                ('News', 'news', True),
                ('Reality-TV', 'reality_tv', True),
                ('Romance', 'romance', True),
                ('Science Fiction', 'sci_fi', True),
                ('Sport', 'sport', True),
                ('Talk-Show', 'talk_show', True),
                ('Thriller', 'thriller', True),
                ('War', 'war', True),
                ('Western', 'western', True)
            ]

            for i in genres: self.list.append(
                {
                    'name': cleangenre.lang(i[0], self.lang),
                    'url': self.genre_link % i[1] if i[2] else self.keyword_link % i[1],
                    'image': 'tvshows.png',
                    'action': 'tvshows'
                })
            
        else:
            genres = tmdbapi.tvGenres()
            for item in genres: self.list.append(
                {
                    'name': item['name'],
                    'url': self.tmdbgenres % ("%s", item['id']),
                    'image': 'tvshows.png',
                    'action': 'tvshows'
                })

        self.addDirectory(self.list)
        return self.list

    def networks(self):
        networks = [
        ('A&E', '/networks/29/ae'),
        ('ABC', '/networks/3/abc'),
        ('AMC', '/networks/20/amc'),
        ('AT-X', '/networks/167/at-x'),
        ('Adult Swim', '/networks/10/adult-swim'),
        ('Amazon', '/webchannels/3/amazon'),
        ('Animal Planet', '/networks/92/animal-planet'),
        ('Audience', '/networks/31/audience-network'),
        ('BBC America', '/networks/15/bbc-america'),
        ('BBC Four', '/networks/51/bbc-four'),
        ('BBC One', '/networks/12/bbc-one'),
        ('BBC Three', '/webchannels/71/bbc-three'),
        ('BBC Two', '/networks/37/bbc-two'),
        ('BET', '/networks/56/bet'),
        ('Bravo', '/networks/52/bravo'),
        ('CBC', '/networks/36/cbc'),
        ('CBS', '/networks/2/cbs'),
        ('CTV', '/networks/48/ctv'),
        ('CW', '/networks/5/the-cw'),
        ('CW Seed', '/webchannels/13/cw-seed'),
        ('Cartoon Network', '/networks/11/cartoon-network'),
        ('Channel 4', '/networks/45/channel-4'),
        ('Channel 5', '/networks/135/channel-5'),
        ('Cinemax', '/networks/19/cinemax'),
        ('Comedy Central', '/networks/23/comedy-central'),
        ('Crackle', '/webchannels/4/crackle'),
        ('Discovery Channel', '/networks/66/discovery-channel'),
        ('Discovery ID', '/networks/89/investigation-discovery'),
        ('Disney Channel', '/networks/78/disney-channel'),
        ('Disney XD', '/networks/25/disney-xd'),
        ('E! Entertainment', '/networks/43/e'),
        ('E4', '/networks/41/e4'),
        ('FOX', '/networks/4/fox'),
        ('FX', '/networks/13/fx'),
        ('Freeform', '/networks/26/freeform'),
        ('HBO', '/networks/8/hbo'),
        ('HGTV', '/networks/192/hgtv'),
        ('Hallmark', '/networks/50/hallmark-channel'),
        ('History Channel', '/networks/53/history'),
        ('ITV', '/networks/35/itv'),
        ('Lifetime', '/networks/18/lifetime'),
        ('MTV', '/networks/22/mtv'),
        ('NBC', '/networks/1/nbc'),
        ('National Geographic', '/networks/42/national-geographic-channel'),
        ('Netflix', '/webchannels/1/netflix'),
        ('Nickelodeon', '/networks/27/nickelodeon'),
        ('PBS', '/networks/85/pbs'),
        ('Showtime', '/networks/9/showtime'),
        ('Sky1', '/networks/63/sky-1'),
        ('Starz', '/networks/17/starz'),
        ('Sundance', '/networks/33/sundance-tv'),
        ('Syfy', '/networks/16/syfy'),
        ('TBS', '/networks/32/tbs'),
        ('TLC', '/networks/80/tlc'),
        ('TNT', '/networks/14/tnt'),
        ('TV Land', '/networks/57/tvland'),
        ('Travel Channel', '/networks/82/travel-channel'),
        ('TruTV', '/networks/84/trutv'),
        ('USA', '/networks/30/usa-network'),
        ('VH1', '/networks/55/vh1'),
        ('WGN', '/networks/28/wgn-america')
        ]

        for i in networks: self.list.append({'name': i[0], 'url': self.tvmaze_link + i[1], 'image': 'networks.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def languages(self):
        languages = [
        ('Arabic', 'ar'),
        ('Bulgarian', 'bg'),
        ('Chinese', 'zh'),
        ('Croatian', 'hr'),
        ('Dutch', 'nl'),
        ('English', 'en'),
        ('Finnish', 'fi'),
        ('French', 'fr'),
        ('German', 'de'),
        ('Greek', 'el'),
        ('Hebrew', 'he'),
        ('Hindi ', 'hi'),
        ('Hungarian', 'hu'),
        ('Icelandic', 'is'),
        ('Italian', 'it'),
        ('Japanese', 'ja'),
        ('Korean', 'ko'),
        ('Norwegian', 'no'),
        ('Persian', 'fa'),
        ('Polish', 'pl'),
        ('Portuguese', 'pt'),
        ('Punjabi', 'pa'),
        ('Romanian', 'ro'),
        ('Russian', 'ru'),
        ('Spanish', 'es'),
        ('Swedish', 'sv'),
        ('Turkish', 'tr'),
        ('Ukrainian', 'uk')
        ]

        for i in languages: self.list.append({'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def certifications(self):
        certificates = ['TV-G', 'TV-PG', 'TV-14', 'TV-MA']

        for i in certificates: self.list.append({'name': str(i), 'url': self.certification_link % str(i).replace('-', '_').lower(), 'image': 'certificates.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def persons(self, url, action):
        if control.setting('tv.list.type') == '0':  
            action = 'tvshows'
            if url == None:
                self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
            else:
                self.list = cache.get(self.imdb_person_list, 1, url)
        else:
            if url == None:
                r = tmdbapi.popularPersons()
                persons = r['results']
                for item in persons:
                    name  = item['name']
                    id    = item['id']
                    try: image = self.tmdb_image + item['profile_path']
                    except: image = control.addonIcon()
                    url   = self.tmdbperson % (id, "%s")
                    self.list.append({'name': name, 'url': url, 'image': image})
            else:
                r = tmdbapi.tmdbRequest(url)
                result = json.loads(r)

                persons = result['results']
                
                page = result.get('page')
                try: totalPages = result.get('total_pages') 
                except: totalPages = '0'
                next = int(page) + 1
                nextPage = 'page=%s' % str(next)
                currPage = re.findall('page=(\d+)', url)[0]
                next = url.replace('page=%s' % currPage, nextPage)
                for item in persons:
                    name  = item['name']
                    id    = item['id']
                    try: image = self.tmdb_image + item['profile_path']
                    except: image = control.addonIcon()
                    u   = self.tmdbperson % (id, "%s")
                    self.list.append({'name': name, 'url': u, 'image': image, 'next': next})                

        for i in range(0, len(self.list)): self.list[i].update({'action': action})
        self.addDirectory(self.list)
        return self.list        
        
    def person(self, url=None):
        try:
            #control.idle()
            action = 'tvPerson'
            if url == None:
                action = 'tvshows'
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                q = k.getText() if k.isConfirmed() else None

                if (q == None or q == ''): return

                if control.setting('tv.list.type') == '0': url = self.persons_link + urllib.parse.quote_plus(q)
                else: url = self.tmdbperson_search %("%s", urllib.parse.quote_plus(q))
            self.persons(url, action)
            #url = '%s?action=moviePersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            #control.execute('Container.Update(%s)' % url)
        except:
            return

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
            if self.imdb_user == '': raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
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
            
            
        try:
            self.list = []
            tmdbCredentials  = True if control.setting('tmdb.session') != '' else False
            if tmdbCredentials == False: raise Exception()
            try:
                userlists += self.tmdb_user_list()

            except:
                pass
        except:
            pass
            

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list
        
        
    def tmdb_user_list(self):
        try:
            items = tmdbapi.account().userlist()
            items = items['results']
            items = [i for i in items if i['list_type'] == 'tv']
        except:
            pass

        for item in items:
            try:
                try:
                    name = item['name']
                    name = "[TMDB] " + name
                except:
                    pass
                name = client.replaceHTMLCodes(name)
                name = normalize_string(name)
                id = item['id']

                url = self.tmdbuserlist_link % (id, "%s")

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list

    def trakt_list(self, url, user):
        try:
            dupes = []

            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.parse.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urllib.parse.urlparse(url).query, '') + '?' + q

            result = trakt.getTraktAsJson(u)

            items = []
            for i in result:
                try: items.append(i['show'])
                except: pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
            if not int(q['limit']) == len(items): raise Exception()
            q.update({'page': str(int(q['page']) + 1)})
            q = (urllib.parse.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urllib.parse.urlparse(url).query, '') + '?' + q
            next = next
        except:
            next = ''

        for item in items:
            try:
                title = item['title']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = normalize_string(title)
                year = item['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                tvdb = item['ids']['tvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))

                if tvdb == None or tvdb == '' or tvdb in dupes: raise Exception()
                dupes.append(tvdb)

                try: premiered = item['first_aired']
                except: premiered = '0'
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'

                try: studio = item['network']
                except: studio = '0'
                if studio == None: studio = '0'

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == None: duration = '0'

                try: rating = str(item['rating'])
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'

                try: votes = str(item['votes'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None: votes = '0'

                try: mpaa = item['certification']
                except: mpaa = '0'
                if mpaa == None: mpaa = '0'

                try: plot = item['overview']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)

                self.list.append({'tvshowtitle': title, 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'next': next})
            except:
                pass

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
                name = normalize_string(name)
                try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except: url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list


    def imdb_list(self, url):
        try:
            r = self.imdb_request(url)
            result = BeautifulSoup(r, "html.parser")
            items = result.find_all('div', class_='lister-item mode-advanced')
            items += result.find_all('div', class_=re.compile('list_item.+?'))
            
        except:
            return

        try:
            next = result.find_all('a', class_= re.compile('.*?next-page'))[0]['href']
            next = url.replace(urllib.parse.urlparse(url).query, urllib.parse.urlparse(next).query)
        except:
            next = ''
            
        for item in items:
            try:
                imdb = re.findall('data-tconst="(tt\d*)"', str(item))[0]
                title = item.find_all('a')[1].getText().strip()
                ##print title
                title = normalize_string(title)
                
                try:
                    try: year = item.find_all('span', class_= re.compile("lister-item-year.*?"))[0].getText()
                    except: year = None
                    if year == '' or year == None:
                        try: year = item.find_all('span', class_='year_type')[0].getText()
                        except: year = '0'
                    try: year = re.findall('(\d{4})', year)[0]
                    except: year = '0'
                except: year = '0'



                try:
                    poster = item.find_all('img')[0]['loadlate']
                except:
                    poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                ##print poster

                try:
                    genre = item.find_all('span', attrs={'class': 'genre'})[0].getText().strip()
                except:
                    genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                ##print genre

                try:
                    duration = item.find_all('span', class_='runtime')[0].getText()
                    duration = re.findall('(\d+?) min(?:s|)', duration)[-1]
                except:
                    duration = '0'
                ##print duration

                rating = '0'
                try:
                    rating = item.find_all('span', attrs={'class': 'rating-rating'})[0]
                except:
                    pass
                try:
                    rating = rating.find_all('span', attrs={'class': 'value'})[0].getText()
                except:
                    rating = '0'
                try:
                    rating = item.find_all('div', attrs={'class': re.compile('.*?imdb-rating')})[0]['data-value']
                except:
                    pass
                if rating == '' or rating == '-': rating = '0'
                ##print rating

                try:
                    votes = item.find_all('div', attrs={'class': re.compile('.*?rating-list')})[0]['title']
                    votes = re.findall('\((.+?) vote(?:s|)\)', str(votes))[0]
                except:
                    try: votes = item.find_all('span', attrs={'name': 'nv'})[0].getText()
                    except: votes = '0'
                    
                    
                if votes == '' or votes == None: votes = '0'
                ##print votes

                try:
                    mpaa = item.find_all('span', attrs={'class': 'certificate'})[0].getText()
                except:
                    mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                ##print mpaa

                try:
                    director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', str(item), re.DOTALL)[0]
                except:
                    director = '0'
                try:
                    dirSoup = BeautifulSoup(director, "html.parser")

                    director = dirSoup.select('a')
                    director = [i.getText() for i in director]
                    director = ' / '.join(director)
                    if director == '': director = '0'
                except:
                    director = '0'
                ##print director

                plot = '0'
                try: plot = item.find_all('p', class_='text-muted')[-1].getText()
                except: pass
                try:plot = item.find_all('div', attrs={'class': 'item_description'})[0].getText()
                except:pass
                
                try: plot = plot.lstrip()
                except:pass
                
                if plot == '': plot = '0'
                ##print plot

                self.list.append(
                        {'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration,
                         'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'plot': plot, 'tagline': '0',
                         'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})

            except:
                pass

        return self.list

    def imdb_userlist(self, url):
        try:
            def imdb_watchlist_id(url):
                return client.parseDOM(self.imdb_request(url), 'meta', ret='content', attrs={'property': 'pageId'})[0]

            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 720, url)
                url = self.imdblist2_link % (url, 'list_order,desc')

            r = self.imdb_request(url)
            result = BeautifulSoup(r, "html.parser")
            items = result.find_all('div', class_='lister-item mode-detail')
        except:
            return
            
        try:
            next = result.find_all('a', class_= re.compile('.*?next-page'))[0]['href']
            next = url.replace(urllib.parse.urlparse(url).query, urllib.parse.urlparse(next).query)
        except:
            next = ''
            
        ##print ("IMDB NEXT PAGE", next)

        for item in items:
            try:
                title = item.find_all('a')[1].getText().strip()
                ##print title
                title = normalize_string(title)
                try:
                    try: year = item.find_all('span', class_= re.compile("lister-item-year.*?"))[0].getText()
                    except: year = None
                    if year == '' or year == None:
                        try: year = item.find_all('span', class_='year_type')[0].getText()
                        except: year = '0'
                    try: year = re.findall('(\d{4})', year)[0]
                    except: year = '0'
                except: year = '0'


                imdb = re.findall('data-tconst="(tt\d*)"', str(item))[0]
                
                try:
                    poster = item.find_all('img')[0]['loadlate']
                except:
                    poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                ##print poster

                try:
                    genre = item.find_all('span', attrs={'class': 'genre'})[0].getText().strip()
                except:
                    genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                ##print genre

                try:
                    duration = item.find_all('span', class_='runtime')[0].getText()
                    duration = re.findall('(\d+?) min(?:s|)', duration)[-1]
                except:
                    duration = '0'
                ##print duration

                rating = '0'
                try:
                    rating = item.find_all('span', attrs={'class': 'rating-rating'})[0]
                except:
                    pass
                try:
                    rating = rating.find_all('span', attrs={'class': 'value'})[0].getText()
                except:
                    rating = '0'
                try:
                    rating = item.find_all('div', attrs={'class': re.compile('.*?imdb-rating')})[0]['data-value']
                except:
                    pass
                if rating == '' or rating == '-': rating = '0'
                ##print rating
                

                try:
                    votes = item.find_all('div', attrs={'class': re.compile('.*?rating-list')})[0]['title']
                    votes = re.findall('\((.+?) vote(?:s|)\)', str(votes))[0]
                except:
                    try: votes = item.find_all('span', attrs={'name': 'nv'})[0].getText()
                    except: votes = '0'
                    
                    
                if votes == '' or votes == None: votes = '0'
                ##print votes

                try:
                    mpaa = item.find_all('span', attrs={'class': 'certificate'})[0].getText()
                except:
                    mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                ##print mpaa

                try:
                    director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', str(item), re.DOTALL)[0]
                except:
                    director = '0'
                try:
                    dirSoup = BeautifulSoup(director, "html.parser")

                    director = dirSoup.select('a')
                    director = [i.getText() for i in director]
                    director = ' / '.join(director)
                    if director == '': director = '0'
                except:
                    director = '0'
                ##print director

                plot = '0'
                try:
                    plot = re.findall('<p class="">(.+?)</p>', str(item), re.DOTALL)[0]
                    plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                except: pass
                
                try: plot = plot.lstrip()
                except:pass
                
                if plot == '': plot = '0'
                ##print plot

                self.list.append(
                        {'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration,
                         'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'plot': plot, 'tagline': '0',
                         'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})

            except:
                pass

        return self.list

    def tmdb_person_list(self, url, matchTitle=None, matchYear=None):

        result = tmdbapi.tmdbRequest(url)
        result = json.loads(result)
        items = result['cast']


        for item in items:
            try:
                title = item['name']
                try:
                    title = client.replaceHTMLCodes(title)
                    title = normalize_string(title)     
                    # title = re.sub(r'[^\x00-\x7f]',r'', title)
                    # title = ' '.join(title.split())
                except:pass
                tmdb = item.get('id')
                tmdb = str(tmdb)
                #print(("TMDB PERSON LIST 2", item))             
                try:originaltitle = item['originaltitle']
                except: originaltitle = title
                #print(("TMDB PERSON LIST 3", originaltitle))                
                year = item['first_air_date']
                try:
                    year = re.compile('(\d{4})').findall(str(year))[0]
                except:
                    year = '0'
                year = year
                #print(("TMDB PERSON LIST 4", year))                 
                if matchTitle != None and matchTitle != '':
                    if cleantitle_get(title) != cleantitle_get(matchTitle): 
                        if cleantitle_get(originaltitle) != cleantitle_get(matchTitle): raise Exception()
                    if not str(year) in matchYear: raise Exception()
                ##print ("4. TMDB MATCHED TITLE", matchTitle, title)     
                
                self.list.append({'title': title, 'originaltitle': originaltitle, 'year': year, 'tmdb': tmdb, 'tvdb': '0'})
            except:
                pass

        return self.list        
        
    def imdb_person_list(self, url):
        try:
            result = self.imdb_request(url)
            items = client.parseDOM(result, 'div', attrs={'class': '.+?detail'})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, 'div', attrs={'class': 'lister-item-content'})[0]
                name = client.parseDOM(name, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name
                

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url

                image = client.parseDOM(item, 'img', ret='src')[0]
                image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
                image = client.replaceHTMLCodes(image)
                image = image

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list


    def imdb_user_list(self, url):
        try:
            result = requests.get(url).content
            items = client.parseDOM(result, 'li', attrs = {'class': '.+?user-list'})
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url.split('/list/', 1)[-1].replace('/', '')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list


    def tvmaze_list(self, url):
        try:
            result = requests.get(url).content
            result = client.parseDOM(result, 'section', attrs = {'id': 'this-seasons-shows'})

            items = client.parseDOM(result, 'div', attrs = {'class': 'content auto cell'})
            items = [client.parseDOM(i, 'a', ret='href') for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = [re.findall('/(\d+)/', i) for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = items[:50]

        except:
            return

        def items_list(i):
            try:
                url = self.tvmaze_info_link % i
                item = requests.get(url).content
                item = json.loads(item)

                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = normalize_string(title)
                year = item['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['externals']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb

                tvdb = item['externals']['thetvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb

                if tvdb == None or tvdb == '': raise Exception()

                try: poster = item['image']['original']
                except: poster = '0'
                if poster == None or poster == '': poster = '0'
                poster = poster

                premiered = item['premiered']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered

                try: studio = item['network']['name']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre

                try: duration = item['runtime']
                except: duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration

                try: rating = item['rating']['average']
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating

                try: plot = item['summary']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                try: plot = plot.lstrip()
                except:pass
                plot = client.replaceHTMLCodes(plot)
                plot = plot
                

                
                try: content = item['type'].lower()
                except: content = '0'
                if content == None or content == '': content = '0'
                content = content
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'tmdb':'0', 'poster': poster, 'content': content})
            except:
                pass

        try:
            threads = []
            for i in items: threads.append(libThread.Thread(items_list, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            filter = [i for i in self.list if i['content'] == 'scripted']
            filter += [i for i in self.list if not i['content'] == 'scripted']
            self.list = filter

            return self.list
        except:
            return


    def worker(self, level=1, limit=False):
        if limit == True: self.limit = True
        self.meta = []
        total = len(self.list)
        
        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        threads = []
        for i in range(0, total + 2):
            if i <= total: threads.append(libThread.Thread(self.super_info, i))
            
        [i.start() for i in threads]
        [i.join() for i in threads]

        if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if i['tvdb'] != '0' and i['tvdb'] != '' and i['tvdb'] != None]

    def super_info(self, i):
        try:    # FORCE CLEARLOGO CHECK
            clearart  = self.list[i]['clearart'] if 'clearart' in self.list[i] else '0'
            clearlogo = self.list[i]['clearlogo'] if 'clearlogo' in self.list[i] else '0'
            banner    = self.list[i]['banner'] if 'banner' in self.list[i] else '0'
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
            tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'
            metalibrary = self.list[i]['metalibrary'] if 'metalibrary' in self.list[i] else False
            if control.setting('fanart.tv.meta') == 'true':
                    try:
                        if clearlogo == '' or clearlogo == None or clearlogo == '0':
                            ftvmeta = fanarttv.get(tvdb, 'tv')
                            if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                            if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                            if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                    except:pass
            self.list[i].update({'clearlogo': clearlogo, 'banner': banner, 'clearart': clearart})
            if self.list[i]['metacache'] == True or metalibrary == True:            
                metaDict = {'clearlogo': clearlogo, 'clearart': clearart, 'banner': banner, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
                self.meta.append(metaDict)
                #print ("USING REMOTEDB META TV")
                raise Exception()
                
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'
            title = self.list[i]['title'] if 'title' in self.list[i] else '0'
            year = self.list[i]['year'] if 'year' in self.list[i] else '0'
            poster = self.list[i]['poster'] if 'poster' in self.list[i] else '0'
            plot = self.list[i]['plot'] if 'plot' in self.list[i] else '0'
            rating = self.list[i]['rating'] if 'rating' in self.list[i] else '0'
            fanart = self.list[i]['fanart'] if 'fanart' in self.list[i] else '0'
            banner = self.list[i]['banner'] if 'banner' in self.list[i] else '0'                                
            premiered = self.list[i]['premiered'] if 'premiered' in self.list[i] else '0'   
            studio = self.list[i]['studio'] if 'studio' in self.list[i] else '0'        
            genre = self.list[i]['genre'] if 'genre' in self.list[i] else '0'
            duration = self.list[i]['duration'] if 'duration' in self.list[i] else '0'  
            votes = self.list[i]['votes'] if 'votes' in self.list[i] else '0'   
            mpaa = self.list[i]['mpaa'] if 'mpaa' in self.list[i] else '0'  
            cast = self.list[i]['cast'] if 'cast' in self.list[i] else '0'              
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'              



            if imdb == '0':
                try:
                    imdb = trakt.SearchTVShow(urllib.parse.quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)[0]
                    imdb = imdb.get('show', '0')
                    imdb = imdb.get('ids', {}).get('imdb', '0')
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                    if not imdb: imdb = '0'
                except:
                    imdb = '0'

            if imdb == '0':
                if tvdb != '0' and tvdb != '' and tvdb != None:
                    try:
                        imdb = tvdbapi.getImdbId(tvdb)
                        if not imdb: imdb = '0'
                    except:
                        imdb = '0'
                    
                    
            if tvdb == '0' or tvdb == '' or tvdb == None:
                if imdb != '0' and imdb != '' and imdb != None:
                    try:
                        u = self.tvdb2_by_imdb % imdb
                        result = tvdbapi.getTvdb(u)
                        item = json.loads(result)
                        item = item['data']
                        tvdb = [x.get('id') for x in item]
                        tvdb = str(tvdb[0])
                    except: tvdb = '0'
                    if tvdb == '': tvdb = '0'
                    tvdb = tvdb
                
                else:
                    url = self.tvdb2_by_query % (urllib.parse.quote_plus(self.list[i]['title']))
                    result = tvdbapi.getTvdb(url)
                    item = json.loads(result)
                    item = item['data']
                    years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]
                    tvdb = [(x, x['seriesName'], x['firstAired']) for x in item]
                    tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1]) and any(y in x[2] for y in years)]
                    tvdb = [x[0] for x in tvdb][0]
                    try: tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(tvdb))[0]
                    except: tvdb = ''
                    if tvdb == '': tvdb = '0'
                    
            # #print ("FANART TV ART 1", self.fanart_tv_user)
            if tvdb == '' or tvdb == None or tvdb == '0': raise Exception()

            try:
                if self.limit == True: raise Exception()
                # IMDB GOT PLOT See full summary click item on some items
                if not 'see full summary' in plot.lower(): raise Exception()
                tmdbInfo = tmdbapi.getImdb(imdb)
                tmdb_info = json.loads(tmdbInfo)
                tmdb_info = tmdb_info['tv_results'][0]
                plot = tmdb_info['overview']
                ##print ("GETTING TMDB OVERVIEW", plot)
            except:
                pass            
            # TRANSLATIONS
            try:
                if self.lang == 'en' or self.lang == 'forced': raise Exception()
                trans_item = tvdbapi.getTvdbTranslation(tvdb)
                trans = json.loads(trans_item)
                title = trans['data']['seriesName']
                plot = trans['data']['overview']
            except:
                pass
                
            poster2 = '0'
            poster3 = '0'
            fanart2 = '0'
            fanart3 = '0'
            clearart = '0'
            banner = '0'    
            clearlogo = '0' 
            discart = '0'           
            metaDB = False  
            
            try:   # CALLING TO API FOR IMAGES
                #if self.limit == True: raise Exception()
                if poster == '' or poster =='0' or poster == None or fanart == '' or fanart =='0' or fanart == None or tmdb == None or tmdb != '':
                    try:
                        tmdbArt = tmdbapi.getImdb(imdb)
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
                                poster = self.tmdb_poster + poster2
                                poster = poster
                        except:
                            pass
                        try:
                            if fanart == '0' or fanart == '' or fanart == None:
                                fanart = tmdbArt['backdrop_path']
                                fanart = self.tmdb_image + fanart
                                fanart = fanart
                        except:
                            fanart = '0'    
                    except:pass

                if poster == '' or poster =='0' or poster == None: poster = tvdbapi.getPoster(tvdb) 
                if fanart == '' or fanart =='0' or fanart == None: fanart = tvdbapi.getFanart(tvdb) 
                # if banner == '' or banner =='0' or banner == None: banner = tvdbapi.getBanner(tvdb)   
                
                if poster == '' or poster =='0' or poster == None or fanart == '' or fanart =='0' or fanart == None:
                    try:
                        ftvmeta = fanarttv.get(tvdb, 'tv')
                        poster3 = ftvmeta['fanart']
                        
                        clearart = ftvmeta['clearart']
                        clearlogo = ftvmeta['clearlogo']
                        
                        if poster == '' or poster == '0' or poster == None: poster = poster3
                        if fanart == '' or fanart == '0' or fanart == None: fanart = ftvmeta['fanart']
                        banner = ftvmeta['banner']
                    except:pass
            except:pass
            
            if tmdb == '0' or tmdb == None:
                try: 
                    tmdbArt = tmdbapi.getTvdb(tvdb)
                    tmdbArt = json.loads(tmdbArt)
                    tmdbArt = tmdbArt['tv_results'][0]
                    tmdb = tmdbArt['id']
                    if tmdb == '' or tmdb == None: tmdb = '0'
                except:
                    pass

                try: 
                    if tmdb != '0' and tmdb != None: raise Exception()
                    tmdbArt = tmdbapi.getImdb(imdb)
                    tmdbArt = json.loads(tmdbArt)
                    tmdbArt = tmdbArt['tv_results'][0]
                    tmdb = tmdbArt['id']
                    if tmdb == '' or tmdb == None: tmdb = '0'
                except:
                    pass
                    
                try:
                    if tmdb != '0' and tmdb != None: raise Exception()
                    tmdb = trakt.SearchTVShow(urllib.parse.quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)[0]
                    tmdb = tmdb.get('show', '0')
                    tmdb = tmdb.get('ids', {}).get('tmdb', '0')
                    if not tmdb: tmdb = '0'
                except:
                    pass                        
                    
            if "http" in poster or "http" in poster2 or "http" in fanart or "http" in fanart2: artmeta = True
            
            if self.limit == True: artmeta = True

            #FINAL CLEARLOGO CHECK
            if control.setting('fanart.tv.meta') == 'true' and artmeta == True:
                try:
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        ftvmeta = fanarttv.get(tvdb, 'tv')
                        if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                        if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                        if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                except:pass
            
            itemdict = {'tvshowtitle': title, 'tagline': '0', 'title': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'poster': poster, 'poster2': poster2, 'poster3': poster3, 'banner': banner, 'fanart': fanart, 'fanart2': fanart2, 'fanart3': fanart3, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot, 'added': self.Today}
            item = dict((k,v) for k, v in itemdict.items() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()
            
            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass
            
    def workerTMDB(self, level=1):
        self.meta = []
        total = len(self.list)

        for i in range(0, total):
            if "tmdb" in self.list[i]: 
                tmdb = str(self.list[i]['tmdb'])
                self.list[i].update({'tmdb': tmdb})
            self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)
        threads = []
        for i in range(0, total + 2):
            if i <= total: threads.append(libThread.Thread(self.super_infoTMDB, i))
        [i.start() for i in threads]
        [i.join() for i in threads]

        if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if not i['tmdb'] == '0']

            
    def super_infoTMDB(self, i):
        try:
            clearart  = self.list[i]['clearart'] if 'clearart' in self.list[i] else '0'
            clearlogo = self.list[i]['clearlogo'] if 'clearlogo' in self.list[i] else '0'
            banner    = self.list[i]['banner'] if 'banner' in self.list[i] else '0'
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
            tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'
            metalibrary = self.list[i]['metalibrary'] if 'metalibrary' in self.list[i] else False
            if control.setting('fanart.tv.meta') == 'true':
                    try:
                        if clearlogo == '' or clearlogo == None or clearlogo == '0':
                            ftvmeta = fanarttv.get(tvdb, 'tv')
                            if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                            if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                            if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                    except:pass
            self.list[i].update({'clearlogo': clearlogo, 'banner': banner, 'clearart': clearart})
            if self.list[i]['metacache'] == True or metalibrary == True:            
                metaDict = {'clearlogo': clearlogo, 'clearart': clearart, 'banner': banner, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
                self.meta.append(metaDict)

                raise Exception()
                
            rating = self.list[i]['rating'] if 'rating' in self.list[i] else '0'
            votes = self.list[i]['votes'] if 'votes' in self.list[i] else '0'
            title = self.list[i]['title'] if 'title' in self.list[i] else '0'
            year = self.list[i]['year'] if 'year' in self.list[i] else '0'
            poster = self.list[i]['poster'] if 'poster' in self.list[i] else '0'
            plot = self.list[i]['plot'] if 'plot' in self.list[i] else '0'
            rating = self.list[i]['rating'] if 'rating' in self.list[i] else '0'
            fanart = self.list[i]['fanart'] if 'fanart' in self.list[i] else '0'
            banner = self.list[i]['banner'] if 'banner' in self.list[i] else '0'
            clearart = self.list[i]['clearart'] if 'clearart' in self.list[i] else '0'
            clearlogo = self.list[i]['clearlogo'] if 'clearlogo' in self.list[i] else '0'

            premiered = self.list[i]['premiered'] if 'premiered' in self.list[i] else '0'
            studio = self.list[i]['studio'] if 'studio' in self.list[i] else '0'
            genre = self.list[i]['genre'] if 'genre' in self.list[i] else '0'
            duration = self.list[i]['duration'] if 'duration' in self.list[i] else '0'
            votes = self.list[i]['votes'] if 'votes' in self.list[i] else '0'
            mpaa = self.list[i]['mpaa'] if 'mpaa' in self.list[i] else '0'
            cast = self.list[i]['cast'] if 'cast' in self.list[i] else '0'
            director = self.list[i]['director'] if 'director' in self.list[i] else '0'
            writer = self.list[i]['writer'] if 'writer' in self.list[i] else '0'
            tagline = self.list[i]['tagline'] if 'tagline' in self.list[i] else '0'

            metaDB = False
            if tmdb == '0': raise Exception()
            details = cache.get(tmdbapi.getDetails, 720, tmdb, True)
            
            # if int(year) > int((self.datetime).strftime('%Y')): raise Exception()
            imdb = details['external_ids']['imdb_id']
            if imdb == '' or imdb == None or imdb == '0': raise Exception()

            poster = details['poster_path']
            if not poster == '' or poster == '0' or poster == None: poster = self.tmdb_poster + poster
            fanart = details['backdrop_path']
            if not fanart == '' or fanart == '0' or fanart == None: fanart = self.tmdb_image + fanart

            try:
                genres = details['genres']
                genre = [x['name'] for x in genres][:3]
                genre = ' / '.join(genre)
            except:
                genre = '0'

            try:
                duration = details.get('episode_run_time')
                duration = duration[0]
            except:
                duration = '0'
            duration = str(duration)

            rating = details.get('vote_average')
            rating = str(rating)
            votes = details.get('vote_count')
            votes = str(votes)

            mpaa = '0'

            try:
                director = details['credits']['crew']
                director = [x['name'] for x in director if x['job'] == 'Director']

                director = ' / '.join(director)
                if director == '': director = '0'
                director = director
            except:
                director = '0'
                

            try:
                tvdb = details['external_ids']['tvdb_id']
            except:
                tvdb = '0'
                

            try:
                premiered = details['first_air_date']
            except:
                premiered = '0'
                
                
            try:
                status = details['status']
            except:
                status = '0'                

            plot = details['overview']
            if plot == '' or plot == None: plot = '0'
            plot = plot

            tagline = '0'
            clearlogo = '0'
            clearart  = '0'
            banner    = '0'
            
            #FINAL CLEARLOGO CHECK
            if control.setting('fanart.tv.meta') == 'true':
                try:
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        ftvmeta = fanarttv.get(tvdb, 'tv')
                        if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                        if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                        if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                except:pass
                    
            item = {'tmdbMeta' : True, 'title': title, 'tvshowtitle': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': str(tmdb), 'tvdb':str(tvdb), 'poster': poster,
                    'poster2': poster, 'poster3': poster, 'banner': banner, 'fanart': fanart, 'fanart2': fanart,
                    'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'genre': genre,
                    'duration': duration, 'rating': rating, 'votes': votes, 'status': status, 'director': director,
                    'writer': writer, 'plot': plot, 'tagline': tagline}
            item = dict((k, v) for k, v in item.items() if not v == '0')
            self.list[i].update(item)
            meta = {'tmdb': str(tmdb), 'tvdb': str(tvdb), 'imdb':str(imdb), 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass

    def favourites(self):
        try:
            items = favourites.getFavourites('tvshows')
            self.list = [i for i in items]
            self.worker()
            self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))  
            self.tvshowDirectory(self.list)
        except:
            return          
            
    def tvshowDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()
        tvtimeToken = control.setting('tvtime.token')
        tmdbCredentials  = True if control.setting('tmdb.session') != '' else False
        showrss = True if control.setting('showrss.password') != '' else False

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        indicators = playcount.getTVShowIndicators(refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

        flatten = True if control.setting('flatten.tvshows') == 'true' else False

        watchedMenu = control.lang(32068) if trakt.getTraktIndicatorsInfo() == True else control.lang(32066)

        unwatchedMenu = control.lang(32069) if trakt.getTraktIndicatorsInfo() == True else control.lang(32067)

        queueMenu = control.lang(32065)

        traktManagerMenu = control.lang(32070)

        nextMenu = control.lang(32053)

        playRandom = control.lang(32535)

        addToLibrary = control.lang(32551)
        
        remoteManagerMenu = 'Remote Library'
        

        for i in items:
            try:
                label = i['title']
                
                if "tmdbMeta" in i: tmdbMeta = 'true'
                else: tmdbMeta = 'false'
                
                try: tmdb = i['tmdb']
                except: tmdb = '0'  
                
                if tmdb != '0' and tmdb != None: tmdbMeta = 'true'

                systitle = sysname = urllib.parse.quote_plus(i['originaltitle'])
                sysimage = urllib.parse.quote_plus(i['poster'])
                imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']
                
                try: tmdb = i['tmdb']
                except: tmdb = '0'

                meta = dict((k,v) for k, v in i.items() if not v == '0')
                

                
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tvdb_id': tvdb})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s&imdb=%s&type=%s' % (sysaddon, urllib.parse.quote_plus(label), imdb, 'tv')})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass


                sysmeta = urllib.parse.quote_plus(json.dumps(meta))
                if flatten == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)
                else:
                    if tmdbMeta != 'true': url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&tmdbMeta=false&meta=%s&tmdb=%s' % (sysaddon, systitle, year, imdb, tvdb, sysmeta, tmdb)
                    else: url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&tmdb=%s&tmdbMeta=true&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, tmdb, sysmeta)

                cm = []
                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tvdb=tvdb, imdb=imdb, tmdb=tmdb))
                    if overlay == 7: 
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&tmdb=%s&query=6)' % (sysaddon, systitle, imdb, tvdb, tmdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else: 
                        cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&tmdb=%s&query=7)' % (sysaddon, systitle, imdb, tvdb, tmdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=season&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s)' % (sysaddon, urllib.parse.quote_plus(systitle), urllib.parse.quote_plus(year), urllib.parse.quote_plus(imdb), urllib.parse.quote_plus(tvdb))))

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
                cm.append(('Trailers', 'RunPlugin(%s?action=trailer&name=%s&imdb=%s&type=%s)' % (sysaddon, urllib.parse.quote_plus(label), imdb, 'tv')))
                if control.setting('remotedb.list') == 'true': cm.append((remoteManagerMenu, 'RunPlugin(%s?action=remoteManager&imdb=%s&tvdb=%s&meta=%s&content=tv)' % (sysaddon, imdb, tvdb, sysmeta)))

                if not action == 'tvFavourites':cm.append(('Add to Local Watchlist', 'RunPlugin(%s?action=addFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))
                if action == 'tvFavourites': cm.append(('Remove From Local Watchlist', 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))

                # if not action == 'tvdbFav':cm.append(('Add To Tvdb', 'RunPlugin(%s?action=tvdbAdd&tvshowtitle=%s&tvdb=%s)' % (sysaddon, systitle, tvdb)))
                # if action == 'tvdbFav': cm.append(('Remove From Tvdb', 'RunPlugin(%s?action=tvdbRemove&tvdb=%s)' % (sysaddon, tvdb)))
                
                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))
                if tmdbCredentials == True:
                    cm.append(('[TMDB] Manager', 'RunPlugin(%s?action=tmdbManager&tmdb=%s&content=tv)' % (
                    sysaddon, tmdb)))
                if tvtimeToken != '' and tvtimeToken != None:
                    cm.append(('Follow in Tvtime', 'RunPlugin(%s?action=tvtimeFollow&tvdb=%s)' % (sysaddon, tvdb)))
                if showrss == True: cm.append(('ShowRSS Manager', 'RunPlugin(%s?action=showrss_manager&name=%s&tvdb=%s)' % (sysaddon, sysname, tvdb)))  
                    
                if isOld == True:
                    cm.append((control.lang2(19033), 'Action(Info)'))

                cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&icon=%s)' % (sysaddon, systitle, year, imdb, tvdb, i['poster'])))

                item = control.item(label=label)

                art = {}

                if 'poster' in i and i['poster'] != '0' and i['poster'] != '' and i['poster'] != None:
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})

                elif 'poster2' in i and i['poster2'] != '0' and i['poster2'] != '' and i['poster2'] != None:
                    art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})

                elif 'poster3' in i and i['poster3'] != '0' and i['poster3'] != '' and i['poster3'] != None:
                    art.update({'icon': i['poster3'], 'thumb': i['poster3'], 'poster': i['poster3']})                   
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                #elif 'banner2' in i and not i['banner2'] == '0':
                    #art.update({'banner': i['banner2']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})

                if settingFanart == 'true' and 'fanart' in i and i['fanart'] != '0' and i['fanart'] != '' and i['fanart'] != None:
                    item.setProperty('Fanart_Image', i['fanart'])
                    
                elif settingFanart == 'true' and 'fanart2' in i and i['fanart2'] != '0' and i['fanart2'] != '' and i['fanart2'] != None:
                    item.setProperty('Fanart_Image', i['fanart2'])

                elif settingFanart == 'true' and 'fanart3' in i and i['fanart3'] != '0' and i['fanart3'] != '' and i['fanart3'] != None:
                    item.setProperty('Fanart_Image', i['fanart3'])

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

        try:
            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=tvshowPage&url=%s' % (sysaddon, urllib.parse.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'tvshows')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('tvshows', {'skin.estuary': 55, 'skin.confluence': 500})


    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065)

        playRandom = control.lang(32535)

        addToLibrary = control.lang(32551)

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

                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=show&url=%s)' % (sysaddon, urllib.parse.quote_plus(i['url']))))

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try: cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowsToLibrary&url=%s)' % (sysaddon, urllib.parse.quote_plus(i['context']))))
                except: pass

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


