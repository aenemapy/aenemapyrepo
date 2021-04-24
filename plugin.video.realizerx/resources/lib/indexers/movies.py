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
from resources.lib.modules import cleangenre, cleantitle
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import views
from resources.lib.modules import utils
from resources.lib.api import tmdbapi, fanarttv
import os, sys, re, json, urllib.request, urllib.parse, urllib.error, urllib.parse, datetime

from resources.lib.modules import metalibrary
import libThread
from resources.lib.modules.lib_titles import cleantitle_get, normalize_string
import requests
from bs4 import BeautifulSoup
params = dict(urllib.parse.parse_qsl(sys.argv[2].replace('?', ''))) if len(sys.argv) > 1 else dict()

action = params.get('action')


class movies:
    def __init__(self):
        self.list = []
        self.remotedbMeta = []
        self.limit = False
        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api.trakt.tv'
        self.tmdb_link = 'https://api.themoviedb.org'

        self.sortby = 'list_order,asc'
        if control.setting('imdb.sortlist') == '0'  : self.sortby = 'list_order,asc'
        elif control.setting('imdb.sortlist') == '1': self.sortby = 'moviemeter,asc'
        elif control.setting('imdb.sortlist') == '2': self.sortby = 'user_rating,desc'
        elif control.setting('imdb.sortlist') == '3': self.sortby = 'alpha,asc'

        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone):
            self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=int(myTimeDelta))
        else:
            self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours=int(myTimeDelta))

        self.Today = (self.datetime).strftime('%Y-%m-%d')
        self.lastYear = (self.datetime - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        self.lastMonth = (self.datetime - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        self.last60days = (self.datetime - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
        self.last180days = (self.datetime - datetime.timedelta(days=180)).strftime('%Y-%m-%d')

        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S')
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.user = 'solaris'
        self.lang = control.apiLanguage()['trakt']
        
        poster_size = ['w154', 'w500', 'original']
        fanart_size = ['w300', 'w1280', 'original']
        
        poster_quality = poster_size[int(control.setting('poster.type'))]
        fanart_quality = fanart_size[int(control.setting('fanart.type'))]
        
        self.tmdb_image = 'https://image.tmdb.org/t/p/%s'  % fanart_quality
        self.tmdb_poster = 'https://image.tmdb.org/t/p/%s' % poster_quality

        self.search_link = 'http://api.trakt.tv/search/movie?limit=20&page=1&query='
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'

        self.tm_img_link = 'https://image.tmdb.org/t/p/w%s%s'

        self.dvd_link = 'http://www.imdb.com/sections/dvd/?ref_=nv_tvv_dvd_6'
        self.persons_link = 'http://www.imdb.com/search/name?count=100&name='
        self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=moviemeter,asc&count=40&start=1'
        self.views_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&sort=num_votes,desc&count=40&start=1'
        self.featured_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=%s,%s&sort=moviemeter,asc&count=40&start=1' % (
        self.lastYear, self.lastMonth)
        self.person_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort=year,desc&count=40&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,%s&genres=%s&sort=moviemeter,asc&count=40&start=1' % (
        self.Today, "%s")
        self.keyword_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,%s&keywords=%s&sort=moviemeter,asc&count=40&start=1' % (
        self.Today, "%s")
        self.language_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort=moviemeter,asc&count=40&start=1'
        self.certification_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=us:%s&sort=moviemeter,asc&count=40&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=40&start=1'
        self.boxoffice_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&count=40&start=1'
        self.oscars_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&groups=oscar_best_picture_winners&sort=year,desc&count=40&start=1'
        self.theaters_link = 'http://www.imdb.com/search/title?title_type=feature&num_votes=1000,&release_date=%s,%s&sort=release_date_us,desc&count=40&start=1' % (self.lastYear, self.Today)
        self.trending_link = 'http://api.trakt.tv/movies/trending?limit=40&page=1'

        
        self.disney_link = 'http://www.imdb.com/search/title?companies=disney&title_type=feature,tv_movie&start=1'
        self.top250_link = 'http://www.imdb.com/search/title?groups=top_250&title_type=feature,tv_movie'
        self.classicscifi_link        = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&release_date=1950-01-01,1980-01-01&genres=sci_fi&languages=en&sort=moviemeter,asc&start=1'
        self.classicadventure_link    = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&release_date=1950-01-01,1980-01-01&genres=adventure&languages=en&sort=moviemeter,asc&start=1'
        self.classiccomedy_link       = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&release_date=1950-01-01,1990-01-01&genres=comedy&languages=en&sort=moviemeter,asc&start=1'
        self.newreleases_link         = 'https://www.imdb.com/search/title?online_availability=US/today/Amazon/paid,US/today/Amazon/subs,US/today/Amazon/subs,UK/today/Amazon/paid,UK/today/Amazon/subs,UK/today/Amazon/subs&title_type=feature,movie,tv_movie&languages=en&num_votes=1000,&production_status=released&release_date=%s,%s&count=50&sort=moviemeter,asc&start=1' % (self.lastYear, self.lastMonth)                   
        self.traktdvd_link            = 'http://api.trakt.tv/calendars/all/dvd/%s/%s?limit=100&page=1' % (self.lastMonth, '30')
        
        

        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api.trakt.tv/users/me/collection/movies'
        self.traktwatchlist_link = 'http://api.trakt.tv/users/me/watchlist/movies'
        self.traktfeatured_link = 'http://api.trakt.tv/recommendations/movies?limit=40'
        self.trakthistory_link = 'http://api.trakt.tv/users/me/history/movies?limit=40&page=1'
        self.traktrecommended_link = 'http://api.trakt.tv/recommendations/movies?limit=100'

        ############# IMDB LISTS ###################
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?sort=%s&st_dt=&mode=detail&title_type=movie,tvMovie,short&page=1' % (
        "%s", self.sortby)
        # list 2 USED TO HARDCODE SORT ORDER i.e. Watchlist
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?sort=%s&st_dt=&mode=detail&title_type=movie,tvMovie,short&page=1' % (
        "%s", "%s")
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=%s&title_type=movie,tvMovie,short&mode=detail&page=1' % (
        self.imdb_user, self.sortby)
        #############################################&title_type=feature,tv_movie,documentary
        self.imdbsearch_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&title=%s&start=1'
        self.imdbadvanced_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&release_date=%s-01-01,%s-01-01&user_rating=%s,10.0&genres=%s&sort=%s&keywords=%s&count=50&start=1'      
        
        # TMDB LISTS
        ############################################
        self.tmdbupcoming_link = 'https://api.themoviedb.org/3/movie/upcoming?api_key=%s&language=en-US&page=1'             
        self.tmdbtoprated_link = 'https://api.themoviedb.org/3/movie/top_rated?api_key=%s&language=en-US&page=1'        
        self.tmdbpopular_link = 'https://api.themoviedb.org/3/movie/popular?api_key=%s&language=en-US&page=1'
        self.tmdbintheaters_link = 'https://api.themoviedb.org/3/movie/now_playing?api_key=%s&language=en-US&page=1'    
        self.tmdbtrending_link = 'https://api.themoviedb.org/3/trending/movie/day?api_key=%s&page=1'
        self.tmdbdvd_link = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&language=en-US&sort_by=popularity.desc&certification_country=US&include_adult=false&include_video=false&primary_release_date.gte=%s&primary_release_date.lte=%s&vote_count.gte=20&with_release_type=4&page=1' % (
        "%s", self.lastYear, self.Today)
        self.tmdbgenres = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&with_genres=%s&page=1'
        self.tmdbperson = 'https://api.themoviedb.org/3/person/%s/movie_credits?api_key=%s&language=en-US'      
        self.tmdbperson_search = 'https://api.themoviedb.org/3/search/person?api_key=%s&language=en-US&query=%s&page=1&include_adult=false'
        self.tmdbfavourites_link = 'https://api.themoviedb.org/3/account/%s/favorite/movies?api_key=%s&session_id=%s&language=en-US&sort_by=created_at.asc&page=1'
        self.tmdbwatchlist_link  = 'https://api.themoviedb.org/3/account/%s/watchlist/movies?api_key=%s&language=en-US&session_id=%s&sort_by=created_at.asc&page=1'
        self.tmdbuserlist_link   = 'https://api.themoviedb.org/3/list/%s?api_key=%s&language=en-US&page=1'
        
    def getSearch(self, title=None):
        try:
            if (title == None or title == ''): return

            url = self.imdbsearch_link % title
            self.list = cache.get(self.imdb_list, 720, url)
            self.list = [i for i in self.list if cleantitle_get(title) == cleantitle_get(i['title'])]
            self.worker()
            return self.list
        except:
            pass
            
    def newMovieSearch(self, title=None):
        try:
            if title == None:
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return
            
            try: 
                cacheID  = 'movie-searchdb'
                searchDB = cache.get_from_string(cacheID, 720, None)
            except: searchDB = []

            if searchDB == None: searchDB = []

            try:
                searchDB = [i for i in searchDB if not i['query'] == title][:19]
                query = {'query' : title}
                searchDB.append(query)
            except:pass
            
            r = cache.get_from_string(cacheID, 720, searchDB, update=True)
            
            if control.setting('movie.list.type') == '1': self.searchTMDB(title=title)
            else: self.search(title=title)      

        except:
            pass            
            
    def movieSearch(self):
        try:
            artPath = control.artPath()
            icon = os.path.join(artPath, 'search.png')
            syshandle = int(sys.argv[1])
            url = '%s?action=newMovieSearch' % (sys.argv[0])
            item = control.item(label='NEW SEARCH >>>') 
            item.setArt({'icon': icon, 'thumb': icon})
            item.setProperty('Fanart_Image', control.addonFanart())
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            
            try: 
                cacheID  = 'movie-searchdb'
                searchDB = cache.get_from_string(cacheID, 720, None)
                searchDB.reverse()
            except: searchDB = []

            if searchDB == None: searchDB = []
            for x in searchDB:
                try:
                    query = x['query']
                    url = '%s?action=newMovieSearch&title=%s' % (sys.argv[0], urllib.parse.quote_plus(query))
                    item = control.item(label=query)    
                    control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
                except: pass

            control.content(syshandle, 'files') 
            control.directory(syshandle, cacheToDisc=True)          

        except:
            pass
            
            
    def getSearchTMDB(self, title=None, year=None, create_directory=False):
        try:
            if (title == None or title == ''): return
            query = cleantitle.query(title)
            years = [str(year), str(int(year)+1), str(int(year)-1)]
            url = 'https://api.themoviedb.org/3/search/movie?api_key=%s&query=%s&page=1' % ("%s", urllib.parse.quote_plus(query))
            self.list = cache.get(self.tmdb_list, 720, url, title, years)

            if len(self.list) <= 0: return None

            self.workerTMDB()
            self.list = [i for i in self.list if cleantitle_get(title.lower()) == cleantitle_get(i['title'].lower())]
            self.list = [i for i in self.list if str(i['year']) in years]
            return self.list
        except: return []

        
    def getCustomLists(self):
        newSearch = True            
        SavedSearches = self.getCustomList()
        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')
        
        url = '%s?action=moviesAdvancedList' % (sysaddon)
        item = control.item(label='NEW SEARCH')
        item.setArt({'icon': addonPoster, 'thumb': addonPoster})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)

        if SavedSearches != None:
            for x in SavedSearches:
                try:
                    name = x['title']
                    link = x['url']
                    id   = x['id']
                    cm = []
                    cm.append(('Delete Search', 'RunPlugin(%s?action=moviesAdvancedListDelete&id=%s)' % (sysaddon, id)))

                    url = '%s?action=moviesAdvancedList&id=%s' % (sysaddon, id)
                    item = control.item(label=name)

                    item.setArt({'icon': addonPoster, 'thumb': addonPoster})
                    if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
                    item.addContextMenuItems(cm)
                    control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
                except:
                    pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)      

            
    def getAdvancedList(self, id=None):
        newSearch = True
        if id != None: url = self.getCustomList(id=id)
            
        try:
            if id != None: raise Exception()
            if newSearch != True: raise Exception()
            genres = ['All','Action','Adventure','Animation','Anime','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','History','Horror','Music', 'Musical','Mystery', 'Romance','Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
            
            genreList = []
            genre_select = control.selectDialog(genres, heading='Genres')
            if genre_select == -1: genre = ''
            else: genre = genres[genre_select]
            genre = re.sub('-','_', genre)
            genre = genre.lower()
            if genre == 'all': genre = ''
            
            if genre != '':
                genreList.append(genre)
                genre_select2 = control.selectDialog(genres, heading='Genres 2')
                if genre_select2 == -1: genre2 = ''         
                else: genre2 = genres[genre_select2]
                genre2 = re.sub('-','_', genre2)            
                genreList.append(genre2)
                
                genre_select3 = control.selectDialog(genres, heading='Genres 3')
                if genre_select3 == -1: genre3 = ''         
                else: genre3 = genres[genre_select3]
                genre3 = re.sub('-','_', genre3)
                genreList.append(genre3)
                genresAll = [i for i in genreList if i != '']
                genre = ",".join(genresAll)
            
            k = control.keyboard('1960', 'From Year');
            k.doModal()
            release_date = k.getText() if k.isConfirmed() else None
            if (release_date == None or release_date == ''): release_date = '1920'
            
            thisYear = (self.datetime).strftime('%Y')
            v = control.keyboard(thisYear, 'To Year');
            v.doModal()
            to_date = v.getText() if v.isConfirmed() else None
            if (to_date == None or to_date == ''): to_date = thisYear
            
            ratings = ['None',
                '1.0',
                '2.0',
                '3.0',
                '4.0', 
                '5.0', 
                '6.0', 
                '6.5', 
                '7.0', 
                '7.5', 
                '8.0', 
                '8.5', 
                '9', 
                '9.5', 
                '10', 
            ]           

            rating_select = control.selectDialog(ratings, heading='Minimum Rating')
            if rating_select == -1: rating = ''
            else: rating = ratings[rating_select]
            
            
            sortings = ['None',
                'Popularity',
                'Year Desc',
                'Year Asc',
            ]                       

            sorting_select = control.selectDialog(sortings, heading='Sort by')
            sorting = sortings[sorting_select]
            sortingLabel = sorting
            if sorting == 'Year Desc':  sorting = 'year,desc'
            elif sorting == 'Year Asc': sorting = 'year,asc'
            else: sorting = 'moviemeter,asc'
            
            
            k = control.keyboard('', 'keywords');
            k.doModal()
            keyword = k.getText() if k.isConfirmed() else None
            if (keyword == None or keyword == ''): keyword = ''         
            
            url = self.imdbadvanced_link % (release_date, to_date, rating, genre, sorting, keyword)
            label = "GENRE: %s | YEAR: %s/%s | RATING: %s | SORT BY: %s | KEYWORDS: %s" 
            title = label % (genre.upper(), release_date, to_date, str(rating), sortingLabel, keyword)
            r = self.saveCustomList(url, str(title))


        except:
            pass
            
        self.list = cache.get(self.imdb_list, 720, url)
        self.worker()
        self.movieDirectory(self.list)          
            
    def saveCustomList(self, url, title, id=None, delete=False):
        customList = control.customSearchList
        if delete == True:
            try:
                with open(customList) as json_file:
                    try:
                        data = json.load(json_file)
                        dataItems = data['items']
                        dataItems = [i for i in dataItems if not i['id'] == id]
                        data = {}
                        data['items'] = dataItems
                    except:
                        data = {}
                        data['items'] = []
            except: 
                data = {}
                data['items'] = []
                
        else:
            try:
                with open(customList) as json_file:
                    try:
                        data = json.load(json_file)
                        dataItems = data['items']
                        if url in dataItems: return
                    except:
                        data = {}
                        data['items'] = []
            except: 
                data = {}
                data['items'] = []
                
            dataItems = data['items']
            
            item = {'title': title, 'url': url, 'id': self.systime}
            dataItems.append(item)
            data['items'] = dataItems
            
        with open(customList, 'w') as outfile: json.dump(data, outfile, indent=2)
        if delete == True: control.refresh()
        return True
        
    def getCustomList(self, id=None):
        customList = control.customSearchList
        try:
            
            with open(customList) as json_file:
                try:
                    data = json.load(json_file)
                    dataItems = data['items']
                    if id != None: 
                        dataItems = [i for i in dataItems if i['id'] == id][0]
                        dataItems = dataItems['url']
                    return dataItems
                except:
                    return None
        except: 
            return None


            
    def traktOnDeck(self):
        from resources.lib.api import trakt
        items = trakt.getTraktAsJson('/sync/playback/movies')

        for item in items:
            try:
                title = item['movie']['title']
                title = client.replaceHTMLCodes(title)

                year = item['movie']['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['movie']['ids']['imdb']
                if imdb == None or imdb == '': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                tmdb = str(item.get('ids', {}).get('tmdb', 0))

                trakt = item['id']

                self.list.append(
                    {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0',
                     'trakt': trakt})
            except:
                pass
        self.worker()
        self.movieDirectory(self.list)

    def get(self, url, idx=True, create_directory=True):
        try:
            try:
                url = getattr(self, url + '_link')
            except:
                pass

            try:
                u = urllib.parse.urlparse(url).netloc.lower()
            except:
                pass

            if u in self.trakt_link and '/users/' in url:
                try:
                    if url == self.trakthistory_link: raise Exception()
                    if not '/users/me/' in url: raise Exception()
                    if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
                except:
                    self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)

                if '/users/me/' in url and '/collection/' in url:
                    self.list = sorted(self.list, key=lambda k: utils.title_key(k['title']))

                if idx == True: self.worker()

            elif u in self.trakt_link and self.search_link in url:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()

            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                if '/user/' in url: self.list = cache.get(self.imdb_userlist, 24, url)
                else: self.list = cache.get(self.imdb_userlist, 720, url)
                #self.list = self.imdb_userlist(url)
                if idx == True: self.worker(limit=True)
                


            elif u in self.imdb_link and not ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 24, url)
                #self.list = self.imdb_list(url)
                if idx == True: self.worker()

            elif u in self.tmdb_link:
                if "with_release_type=" in url: self.list = cache.get(self.getTmdbReleases, 24, url)
                elif "/person/" in url: self.list = cache.get(self.tmdb_person_list, 24, url)
                else: 
                    cacheTime = 24
                    if "/account/" in url: cacheTime = 0
                    if "/list/" in url: cacheTime = 0
                    self.list = cache.get(self.tmdb_list, cacheTime, url)
                self.workerTMDB()

            if idx == True and create_directory == True: self.movieDirectory(self.list)
            return self.list
        except:
            pass

    def imdb_request(self, url):
        headers = {'Accept-Language': 'en'}
        try:r = requests.get(url, headers=headers, timeout=30).content
        except requests.Timeout as err: control.infoDialog('IMDB is Slow or Down, Please Try Later...')
        return r
        
    def getTmdbReleases(self, url):
        result = tmdbapi.tmdbRequest(url)
        result = json.loads(result)
        items = result['results']
        dateNow = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        dateNow = datetime.date(*list(map(int, dateNow.split('-'))))
        for item in items:
            try:
                page = result.get('page')
                try: totalPages = result.get('total_pages') 
                except: totalPages = '0'
                

                next = int(page) + 1
                nextPage = 'page=%s' % str(next)
                currPage = re.findall('page=(\d+)', url)[0]

                next = url.replace('page=%s' % currPage, nextPage)
                
                if int(page) >= int(totalPages) : next = '0'
                
                title = item['title']
                title = title
                title = client.replaceHTMLCodes(title)
                title = normalize_string(title)             
                tmdb = item.get('id')
                tmdb = str(tmdb)

                    
                year = item['release_date']
                try:
                    year = re.compile('(\d{4})').findall(str(year))[0]
                except:
                    year = '0'
                year = year

                details = tmdbapi.getDetails(tmdb)
                rDates = []
                releaseDates = details['release_dates']['results']
                releases = [i for i in releaseDates if i['iso_3166_1'] == 'US' or i['iso_3166_1'] == 'GB']
                releases = [i['release_dates'] for i in releases]
                for x in releases:
                    rDates += [i['release_date'] for i in x if int(i['type']) >= 4]
               
                Released = False
                for y in rDates:
                    relDate = re.compile('(\d{4}-\d{2}-\d{2})').findall(y)[0]
                    nDate = datetime.date(*list(map(int, relDate.split('-'))))
                    newDate = nDate - datetime.timedelta(days=14)

                    if newDate <= dateNow: Released = True
                    # #print "DATE CHECK"
                    # #print title, dateNow, newDate, Released   
                    
                if Released == False: raise Exception()
                    
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'tmdb': tmdb, 'tvdb': '0', 'next': next})
            except:
                pass

        return self.list
        


    def remotedb_meta(self, imdb=None, tmdb=None):
        try:
            if control.setting('local.meta') != 'true': return None
            dbmeta = metalibrary.metaMovies(imdb=imdb, tmdb=tmdb)
            return dbmeta
            
        except:pass
        
    def remotedb_addmeta(self, type, meta):
        try:
            from resources.lib.api import remotedb
            dbm = remotedb.add_metadata(type, meta)
        except:pass
        
    def widget(self):
        setting = control.setting('movie.widget')

        if setting == '2':
            self.get(self.trending_link)
        elif setting == '3':
            self.get(self.popular_link)
        elif setting == '4':
            self.get(self.theaters_link)
        else:
            self.get(self.featured_link)

    def search(self, title=None, create_directory=False):
        try:
            if title == None:
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return
                
            url = self.imdbsearch_link % urllib.parse.quote_plus(title)
            self.get(url)

        except:
            pass
            
    def searchTMDB(self, title=None, create_directory=False):
        try:
            if title == None:
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                title = k.getText() if k.isConfirmed() else None
                if (title == None or title == ''): return
                
            u = 'https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1' % ("%s", title)
            self.get(u)
        except: pass

    def person(self, url=None):
        try:
            #control.idle()
            action = 'moviePerson'
            if url == None:
                action = 'movies'
                t = control.lang(32010)
                k = control.keyboard('', t);
                k.doModal()
                q = k.getText() if k.isConfirmed() else None

                if (q == None or q == ''): return

                if control.setting('movie.list.type') == '0': url = self.persons_link + urllib.parse.quote_plus(q)
                else: url = self.tmdbperson_search %("%s", urllib.parse.quote_plus(q))
            self.persons(url, action)
            #url = '%s?action=moviePersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            #control.execute('Container.Update(%s)' % url)
        except:
            return

    def genres(self):
        if control.setting('movie.list.type') == '0':
            genres = [
                ('Action', 'action', True),
                ('Adventure', 'adventure', True),
                ('Animation', 'animation', True),
                ('Anime', 'anime', False),
                ('Biography', 'biography', True),
                ('Comedy', 'comedy', True),
                ('Crime', 'crime', True),
                ('Documentary', 'documentary', True),
                ('Drama', 'drama', True),
                ('Family', 'family', True),
                ('Fantasy', 'fantasy', True),
                ('History', 'history', True),
                ('Horror', 'horror', True),
                ('Music ', 'music', True),
                ('Musical', 'musical', True),
                ('Mystery', 'mystery', True),
                ('Romance', 'romance', True),
                ('Science Fiction', 'sci_fi', True),
                ('Sport', 'sport', True),
                ('Thriller', 'thriller', True),
                ('War', 'war', True),
                ('Western', 'western', True)
            ]

            
            for i in genres: self.list.append(
                {
                    'name': cleangenre.lang(i[0], self.lang),
                    'url': self.genre_link % i[1] if i[2] else self.keyword_link % i[1],
                    'image': 'movies.png',
                    'action': 'movies'
                })
                

        else:
            genres = tmdbapi.movieGenres()
            for item in genres: self.list.append(
                {
                    'name': item['name'],
                    'url': self.tmdbgenres % ("%s", item['id']),
                    'image': 'movies.png',
                    'action': 'movies'
                })

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

        for i in languages: self.list.append(
            {'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list

    def certifications(self):
        certificates = ['G', 'PG', 'PG-13', 'R', 'NC-17']

        for i in certificates: self.list.append(
            {'name': str(i), 'url': self.certification_link % str(i).replace('-', '_').lower(),
             'image': 'certificates.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list

    def years(self):
        year = (self.datetime.strftime('%Y'))

        for i in range(int(year) - 0, 1900, -1): self.list.append(
            {'name': str(i), 'url': self.year_link % (str(i), str(i)), 'image': 'years.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list

    def persons(self, url, action):
        if control.setting('movie.list.type') == '0':   
            action = 'movies'
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
                if activity > cache.timeout(self.trakt_user_list, self.traktlists_link,
                                            self.trakt_user): raise Exception()
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
                if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link,
                                            self.trakt_user): raise Exception()
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
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'movies'})
        self.addDirectory(self.list, queue=True)
        return self.list

    def trakt_list(self, url, user):
        try:
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.parse.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urllib.parse.urlparse(url).query, '') + '?' + q

            result = trakt.getTraktAsJson(u)

            items = []
            for i in result:
                try:
                    items.append(i['movie'])
                except:
                    pass
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
                title = client.replaceHTMLCodes(title)
                title = normalize_string(title) 
                year = item['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                        
                tmdb = str(item.get('ids', {}).get('tmdb', 0))

                try:
                    premiered = item['released']
                except:
                    premiered = '0'
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'

                try:
                    genre = item['genres']
                except:
                    genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)

                try:
                    duration = str(item['runtime'])
                except:
                    duration = '0'
                if duration == None: duration = '0'

                try:
                    rating = str(item['rating'])
                except:
                    rating = '0'
                if rating == None or rating == '0.0': rating = '0'

                try:
                    votes = str(item['votes'])
                except:
                    votes = '0'
                try:
                    votes = str(format(int(votes), ',d'))
                except:
                    pass
                if votes == None: votes = '0'

                try:
                    mpaa = item['certification']
                except:
                    mpaa = '0'
                if mpaa == None: mpaa = '0'

                try:
                    plot = item['overview']
                except:
                    plot = '0'
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)

                try:
                    tagline = item['tagline']
                except:
                    tagline = '0'
                if tagline == None: tagline = '0'
                tagline = client.replaceHTMLCodes(tagline)

                self.list.append(
                    {'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'genre': genre,
                     'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot,
                     'tagline': tagline, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': '0', 'fanart': '0',
                     'next': next})
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
                try:
                    name = item['list']['name']
                except:
                    name = item['name']
                name = client.replaceHTMLCodes(name)
                name = normalize_string(name)
                try:
                    url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except:
                    url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list
        
    def tmdb_user_list(self):
        try:
            items = tmdbapi.account().userlist()
            items = items['results']
            items = [i for i in items if i['list_type'] == 'movie']
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

    def tmdb_list(self, url, matchTitle=None, matchYear=None):
        if "/account/" in url: 
            result = tmdbapi.account().request(url)
            
        else:
            result = tmdbapi.tmdbRequest(url)
            #print ("TMDB API REQUEST MOVIES")
            #print (result)
            result = json.loads(result)
            #print ("TMDB API REQUEST MOVIES 2")
            #print (result)
            
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
                
                title = item['title']
                try:
                    title = client.replaceHTMLCodes(title)
                    title = normalize_string(title)     
                    # title = re.sub(r'[^\x00-\x7f]',r'', title)
                    # title = ' '.join(title.split())
                except:pass
                tmdb = item.get('id')
                tmdb = str(tmdb)
                
                try:originaltitle = item['originaltitle']
                except: originaltitle = title
                
                year = item['release_date']
                try:
                    year = re.compile('(\d{4})').findall(str(year))[0]
                except:
                    year = '0'
                year = year
                
                if matchTitle != None and matchTitle != '':
                    if cleantitle_get(title) != cleantitle_get(matchTitle): 
                        if cleantitle_get(originaltitle) != cleantitle_get(matchTitle): raise Exception()
                    if not str(year) in matchYear: raise Exception()
                #print ("4. TMDB MATCHED TITLE")     
        
                self.list.append({'title': title, 'originaltitle': originaltitle, 'year': year, 'tmdb': tmdb, 'tvdb': '0', 'next': next})
            except:
                pass

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
            
        ##print ("IMDB NEXT PAGE", next)

        for item in items:
            try:

                imdb = re.findall('data-tconst="(tt\d*)"', str(item))[0]


                title = item.find_all('a')[1].getText().strip() 
                title = client.replaceHTMLCodes(title)
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

                ##print imdb

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
                try:
                    plot = re.sub('\n', '', plot)
                    plot = plot.lstrip()
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
                title = client.replaceHTMLCodes(title)
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
                    plot = plot.lstrip()
                except: pass

                if plot == '': plot = '0'
                ##print plot

                self.list.append(
                        {'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration,
                         'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'plot': plot, 'tagline': '0',
                         'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})

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
        
    def tmdb_person_list(self, url, matchTitle=None, matchYear=None):
        result = tmdbapi.tmdbRequest(url)
        result = json.loads(result)
        items = result['cast']

        for item in items:
            try:
        
                title = item['title']
                try:
                    title = client.replaceHTMLCodes(title)
                    title = normalize_string(title)     
                    # title = re.sub(r'[^\x00-\x7f]',r'', title)
                    # title = ' '.join(title.split())
                except:pass
                tmdb = item.get('id')
                tmdb = str(tmdb)
                
                try:originaltitle = item['originaltitle']
                except: originaltitle = title
                
                year = item['release_date']
                try:
                    year = re.compile('(\d{4})').findall(str(year))[0]
                except:
                    year = '0'
                year = year
                
                if matchTitle != None and matchTitle != '':
                    if cleantitle_get(title) != cleantitle_get(matchTitle): 
                        if cleantitle_get(originaltitle) != cleantitle_get(matchTitle): raise Exception()
                    if not str(year) in matchYear: raise Exception()
                ##print ("4. TMDB MATCHED TITLE", matchTitle, title)     
                

                    
                self.list.append({'title': title, 'originaltitle': originaltitle, 'year': year, 'tmdb': tmdb, 'tvdb': '0'})
            except:
                pass

        return self.list

    def imdb_user_list(self, url):
        try:
            result = requests.get(url).content
            items = client.parseDOM(result, 'li', attrs={'class': '.+?user-list'})
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

    def inProgress(self):
        try:
            if control.setting('inprogress.type') == '1':
                from resources.lib.api import remotedb
                type = 'movies'
                remotedb.getInProgress(type)
                raise Exception()
                
            if control.setting('inprogress.type') == '2':
                self.traktOnDeck()
                raise Exception()               

            from resources.lib.modules import favourites
            items = favourites.getProgress('movies')
            self.list = [i[1] for i in items]
            try: self.list.reverse()
            except: pass

            self.worker()
            self.movieDirectory(self.list)
        except:
            return

    def worker(self, limit=False):
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

        self.list = [i for i in self.list if not i['imdb'] == '0']

        # self.list = metacache.local(self.list, self.tm_img_link, 'poster3', 'fanart2')

        # if self.fanart_tv_user == '':
            # for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})

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

        # self.list = metacache.local(self.list, self.tm_img_link, 'poster3', 'fanart2')

        # if self.fanart_tv_user == '':
            # for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})

    def favourites(self):
        from resources.lib.modules import favourites
        try:
            items = favourites.getFavourites('movies')
            self.list = [i for i in items]
            self.worker()
            self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))
            self.movieDirectory(self.list)
        except:
            return

    def super_infoTMDB(self, i):
        try:
            # FORCE CLEARLOGO UPDATE
            clearart  = self.list[i]['clearart'] if 'clearart' in self.list[i] else '0'
            clearlogo = self.list[i]['clearlogo'] if 'clearlogo' in self.list[i] else '0'
            banner    = self.list[i]['banner'] if 'banner' in self.list[i] else '0'
            discart   = self.list[i]['discart'] if 'discart' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            metalibrary = self.list[i]['metalibrary'] if 'metalibrary' in self.list[i] else False
            if control.setting('fanart.tv.meta') == 'true':
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        try:
                            ftvmeta = fanarttv.get(tmdb, 'movies')
                            if ftvmeta == None: raise Exception()
                            if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                            if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                            if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                            if discart == '' or discart == None or discart == '0': discart = ftvmeta['discart']
                        except: pass    
            self.list[i].update({'clearlogo': clearlogo, 'banner': banner, 'discart': discart, 'clearart': clearart})
            if self.list[i]['metacache'] == True or metalibrary == True:
                metaDict = {'clearlogo': clearlogo, 'banner': banner, 'discart': discart, 'clearart': clearart, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
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
            discart = self.list[i]['discart'] if 'discart' in self.list[i] else '0'
            originaltitle = self.list[i]['originaltitle'] if 'originaltitle' in self.list[i] else 'title'
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
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'

            if tmdb == '0': raise Exception()
            details = cache.get(tmdbapi.getDetails, 720, tmdb)

            # if int(year) > int((self.datetime).strftime('%Y')): raise Exception()
            imdb = details['imdb_id']
            if imdb == '' or imdb == None or imdb == '0': raise Exception()

            metaDB = False
                
            if metaDB == False:
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
                duration = details.get('runtime')
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

            plot = details['overview']
            if plot == '' or plot == None: plot = '0'
            plot = plot

            tagline = details['tagline']
            if tagline == '' or tagline == None: tagline = '0'
            tagline = tagline

            #FINAL CLEARLOGO CHECK
            if control.setting('fanart.tv.meta') == 'true':
                try:
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        ftvmeta = fanarttv.get(tmdb, 'movies')
                        if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                        if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                        if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                        if discart == '' or discart == None or discart == '0': discart = ftvmeta['discart'] 
                except:pass
            
            item = {'title': title, 'originaltitle': originaltitle, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster,
                    'poster2': poster, 'poster3': poster, 'banner': banner, 'fanart': fanart, 'fanart2': fanart,
                    'clearlogo': clearlogo, 'discart': discart, 'clearart': clearart, 'premiered': premiered, 'genre': genre,
                    'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director,
                    'writer': writer, 'plot': plot, 'tagline': tagline}
            item = dict((k, v) for k, v in item.items() if not v == '0')
            self.list[i].update(item)
            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass

    def super_info(self, i):
        try:
            # FORCE CLEARLOGO UPDATE
            clearart  = self.list[i]['clearart'] if 'clearart' in self.list[i] else '0'
            clearlogo = self.list[i]['clearlogo'] if 'clearlogo' in self.list[i] else '0'
            banner    = self.list[i]['banner'] if 'banner' in self.list[i] else '0'
            discart   = self.list[i]['discart'] if 'discart' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            metalibrary = self.list[i]['metalibrary'] if 'metalibrary' in self.list[i] else False
            if control.setting('fanart.tv.meta') == 'true':
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        try:
                            ftvmeta = fanarttv.get(imdb, 'movies')
                            if ftvmeta == None: raise Exception()
                            if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                            if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                            if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                            if discart == '' or discart == None or discart == '0': discart = ftvmeta['discart']
                        except: pass    
            self.list[i].update({'clearlogo': clearlogo, 'banner': banner, 'discart': discart, 'clearart': clearart})
            if self.list[i]['metacache'] == True or metalibrary == True:
                metaDict = {'clearlogo': clearlogo, 'banner': banner, 'discart': discart, 'clearart': clearart, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
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
            discart = self.list[i]['discart'] if 'discart' in self.list[i] else '0'

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
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'

            artmeta = True
            tmdbInfo = None
            # LANGUAGE TRANSLATION
            try:
                ##print ("KODI SELF LANGUAGE", self.lang)
                if self.lang == 'en': raise Exception()
                if self.lang == 'forced': trans_lang = 'en'

                item = trakt.getMovieSummary(imdb)              
                if trans_lang not in item.get('available_translations', [trans_lang]): raise Exception()
                trans_item = trakt.getMovieTranslation(imdb, trans_lang, full=True)
  
                title = trans_item.get('title') or title
                tagline = trans_item.get('tagline') or tagline
                plot = trans_item.get('overview') or plot
            except:
                pass

            try:
                if self.limit == True: raise Exception()
                # IMDB GOT PLOT See full summary click item on some items
                if not 'see full summary' in plot.lower(): raise Exception()
                tmdbInfo = tmdbapi.getImdb(imdb)
                tmdb_info = json.loads(tmdbInfo)
                tmdb_info = tmdb_info['movie_results'][0]
                plot = tmdb_info['overview']
                ##print ("GETTING TMDB OVERVIEW", plot)
            except:
                pass
                
            poster2 = '0'
            poster3 = '0'
            fanart2 = '0'
            fanart3 = '0'
                
            try:
                #if self.limit == True: raise Exception()
                if fanart == '0' or fanart == '' or fanart == None or poster == '' or poster == None or poster == '0':
                    if tmdbInfo != None: tmdbArt = tmdbInfo
                    else: tmdbArt = tmdbapi.getImdb(imdb)
                    try:
                        tmdbArt = json.loads(tmdbArt)
                        #print(tmdbArt)
                        tmdbArt = tmdbArt['movie_results'][0]
                    except:
                        artmeta = False

                    try:
                        tmdb = tmdbArt['id']
                        if tmdb == '' or tmdb == None: tmdb = self.list[i]['tmdb']
                    # if "http" in poster2: poster = poster2
                    except:
                        pass

                    try:
                        poster2 = tmdbArt['poster_path']
                        if poster2 == '' or poster2 == None: poster2 = '0'
                        if not poster2 == '0': poster2 = self.tmdb_poster + poster2
                        poster2 = poster2
                        if "http" in poster2: poster = poster2
                    except:
                        poster2 = '0'

                    try:
                        fanart = tmdbArt['backdrop_path']
                        if fanart == '' or fanart == None: fanart = '0'
                        if not fanart == '0': fanart = self.tmdb_image + fanart
                        fanart = fanart
                    except:
                        fanart = '0'

                if fanart == '0' or fanart == '' or fanart == None or poster == '' or poster == None or poster == '0':
                    ftvmeta = fanarttv.get(imdb, 'movies')
                    clearart = ftvmeta['clearart']
                    clearlogo = ftvmeta['clearlogo']
                    discart = ftvmeta['discart']
                    poster3 = ftvmeta['poster']
                    if poster == '' or poster == '0' or poster == None: poster = poster3
                    if fanart == '' or fanart == '0' or fanart == None: fanart = ftvmeta['fanart']
                    banner = ftvmeta['banner']
            except:pass
                
            if "http" in poster or "http" in poster2 or "http" in fanart or "http" in fanart2: artmeta = True
            if self.limit == True: artmeta = True
            
            #FINAL CLEARLOGO CHECK
            if control.setting('fanart.tv.meta') == 'true' and artmeta == True:
                try:
                    if clearlogo == '' or clearlogo == None or clearlogo == '0':
                        ftvmeta = fanarttv.get(imdb, 'movies')
                        if clearlogo == '' or clearlogo == None or clearlogo == '0': clearlogo = ftvmeta['clearlogo']
                        if clearart == '' or clearart == None or clearart == '0': clearart = ftvmeta['clearart']
                        if banner == '' or banner == None or banner == '0': banner = ftvmeta['banner']
                        if discart == '' or discart == None or discart == '0': discart = ftvmeta['discart']
                except:pass
    
            itemdict = {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster,
                    'poster2': poster2, 'poster3': poster3, 'banner': banner, 'fanart': fanart, 'fanart2': fanart2, 'studio': studio, 
                    'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'premiered': premiered, 'genre': genre,
                    'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'studio': studio, 
                    'writer': writer, 'plot': plot, 'tagline': tagline, 'added': self.Today}

            item = dict((k, v) for k, v in itemdict.items() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()
            
            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass

    def movieDirectory(self, items):
        if items == None or len(items) == 0: control.idle(); sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()
        tmdbCredentials  = True if control.setting('tmdb.session') != '' else False
        try:
            isOld = False; control.item().getArt('type')
        except:
            isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getMovieIndicators(refresh=True) if action == 'movies' else playcount.getMovieIndicators()

        playbackMenu = control.lang(32063) if control.setting('hosts.mode') == '2' or control.setting('hosts.mode') == '3' else control.lang(32064)

        watchedMenu = control.lang(32068) if trakt.getTraktIndicatorsInfo() == True else control.lang(
            32066)

        unwatchedMenu = control.lang(32069) if trakt.getTraktIndicatorsInfo() == True else control.lang(
            32067)

        queueMenu = control.lang(32065)

        traktManagerMenu = control.lang(32070)

        remoteManagerMenu = 'Remote Library'

        nextMenu = control.lang(32053)

        addToLibrary = control.lang(32551)

        for i in items:
            try:
                if i['title'] != i['originaltitle']:
                    title = i['originaltitle']
                else:
                    title = i['title']
                label = '%s' % (title)
                imdb, tmdb, year = i['imdb'], i['tmdb'], i['year']
                sysname = urllib.parse.quote_plus('%s (%s)' % (title, year))

                try:
                    traktID = i['trakt']
                except:
                    traktID = ''
                    
                try: tmdb = i['tmdb']
                except: tmdb = '0'

                systitle = urllib.parse.quote_plus(title)

                meta = dict((k, v) for k, v in i.items() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tmdb_id': tmdb})
                meta.update({'mediatype': 'movie'})
                trailerName = '%s %s' % (title, year)
                meta.update({'trailer': '%s?action=trailer&name=%s&imdb=%s&type=%s' % (sysaddon, urllib.parse.quote_plus(trailerName), imdb, 'movie')})
                # meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not 'duration' in i:
                    meta.update({'duration': '120'})
                elif i['duration'] == '0':
                    meta.update({'duration': '120'})
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                try:
                    meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except:
                    pass

                poster = [i[x] for x in ['poster3', 'poster', 'poster2'] if i.get(x, '0') != '0']
                poster = poster[0]
                if poster == '' or poster == '0' or poster == None: poster = addonPoster

                sysmeta = urllib.parse.quote_plus(json.dumps(meta))

                url = '%s?action=play&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s' % (
                sysaddon, systitle, year, imdb, tmdb, sysmeta)
                sysurl = urllib.parse.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)
                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
                cm.append(('Trailers', 'RunPlugin(%s?action=trailer&name=%s&imdb=%s&type=%s)' % (sysaddon, urllib.parse.quote_plus(trailerName), imdb, 'movie')))
                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb=imdb, tmdb=tmdb))
                    if overlay == 7:
                        cm.append(
                            (unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&tmdb=%s&query=6)' % (sysaddon, imdb, tmdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append(
                            (watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&tmdb=%s&query=7)' % (sysaddon, imdb, tmdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                if control.setting('remotedb.list') == 'true': cm.append((remoteManagerMenu,
                                                                          'RunPlugin(%s?action=remoteManager&imdb=%s&tmdb=%s&meta=%s&content=movie)' % (
                                                                          sysaddon, imdb, tmdb, sysmeta)))

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (
                    sysaddon, sysname, imdb)))

                if tmdbCredentials == True:
                    cm.append(('[TMDB] Manager', 'RunPlugin(%s?action=tmdbManager&tmdb=%s&content=movie)' % (
                    sysaddon, tmdb)))
                
                cm.append(('Info (Old)', 'Action(Info)'))

                cm.append((addToLibrary,
                           'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s&icon=%s)' % (
                           sysaddon, sysname, systitle, year, imdb, tmdb, poster)))
                if action == 'moviesInProgress': cm.append(('Remove From Progress',
                                                            'RunPlugin(%s?action=deleteProgress&meta=%s&content=movies)' % (
                                                            sysaddon, sysmeta)))
                if action == 'traktOnDeck': cm.append(('Remove From Trakt Progress',
                                                       'RunPlugin(%s?action=traktOnDeckRemove&trakt=%s)' % (
                                                       sysaddon, traktID)))
                if not action == 'movieFavourites': cm.append(('Add to Local Watchlist',
                                                               'RunPlugin(%s?action=addFavourite&meta=%s&content=movies)' % (
                                                               sysaddon, sysmeta)))
                if action == 'movieFavourites': cm.append(('Remove From Local Watchlist',
                                                           'RunPlugin(%s?action=deleteFavourite&meta=%s&content=movies)' % (
                                                           sysaddon, sysmeta)))
                cm.append(
                    (playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                item = control.item(label=label)

                art = {}
                if 'poster' in i and i['poster'] != '0' and i['poster'] != '' and i['poster'] != None:
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})

                elif 'poster2' in i and i['poster2'] != '0' and i['poster2'] != '' and i['poster2'] != None:
                    art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                    
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
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

                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)

                item.addContextMenuItems(cm)
                # item.setProperty('IsPlayable', isPlayable)

                # played = bookmarks.bookmarks().get(bookmarkname.lower())
                # item.setProperty('resumetime', played)

                item.setInfo(type='Video', infoLabels=meta)

                # video_streaminfo = {'codec': 'bluray', 'audio' : 'avc'}
                # item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=moviePage&url=%s' % (sysaddon, urllib.parse.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})

    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle(); sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065)

        playRandom = control.lang(32535)

        addToLibrary = control.lang(32551)
        nextMenu = 'NEXT >>>'
        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'):
                    thumb = i['image']
                elif not artPath == None:
                    thumb = os.path.join(artPath, i['image'])
                else:
                    thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try:
                    url += '&url=%s' % urllib.parse.quote_plus(i['url'])
                except:
                    pass

                cm = []

                cm.append((playRandom,
                           'RunPlugin(%s?action=random&rtype=movie&url=%s)' % (sysaddon, urllib.parse.quote_plus(i['url']))))

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try:
                    cm.append((addToLibrary, 'RunPlugin(%s?action=moviesToLibrary&url=%s)' % (
                    sysaddon, urllib.parse.quote_plus(i['context']))))
                except:
                    pass

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        try:

            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=%s&url=%s' % (sysaddon, items[0]['action'], urllib.parse.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass
            
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)
