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


from resources.lib.api import trakt
from resources.lib.modules import cleangenre
from resources.lib.modules import cleantitle
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import utils
from resources.lib.modules import bookmarks
from resources.lib.modules import favourites

from resources.lib.api import tmdbapi, fanarttv
import os,sys,re,json,urllib,urlparse,datetime
import requests
import metalibrary
import libThread
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

import requests

class movies:
    def __init__(self):
        self.list = []

        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api.trakt.tv'
        self.tmdb_link = 'https://api.themoviedb.org'



        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone): self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
        else: self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))	
		
        self.Today = (self.datetime).strftime('%Y-%m-%d')
        self.lastYear = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.lastMonth = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.last60days = (self.datetime - datetime.timedelta(days = 60)).strftime('%Y-%m-%d')
        self.last180days = (self.datetime - datetime.timedelta(days = 180)).strftime('%Y-%m-%d')

        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.user = 'realizer'
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
        self.featured_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=%s,%s&sort=moviemeter,asc&count=40&start=1' % (self.lastYear, self.lastMonth)
        self.person_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort=year,desc&count=40&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,%s&genres=%s&sort=moviemeter,asc&count=40&start=1' % (self.Today, "%s")
        self.keyword_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,%s&keywords=%s&sort=moviemeter,asc&count=40&start=1' % (self.Today, "%s")
        self.language_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort=moviemeter,asc&count=40&start=1'
        self.certification_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=us:%s&sort=moviemeter,asc&count=40&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=40&start=1'
        self.boxoffice_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&count=40&start=1'
        self.oscars_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&groups=oscar_best_picture_winners&sort=year,desc&count=40&start=1'
        self.theaters_link = 'http://www.imdb.com/search/title?title_type=feature&num_votes=1000,&release_date=%s,%s&sort=release_date_us,desc&count=40&start=1' % (self.lastYear, self.Today)
        self.trending_link = 'http://api.trakt.tv/movies/trending?limit=40&page=1'
        self.newreleases_link         = 'https://www.imdb.com/search/title?online_availability=US/today/Amazon/paid,US/today/Amazon/subs,US/today/Amazon/subs,UK/today/Amazon/paid,UK/today/Amazon/subs,UK/today/Amazon/subs&title_type=feature,movie,tv_movie&languages=en&num_votes=1000,&production_status=released&release_date=%s,%s&count=50&sort=moviemeter,asc&start=1'	% (self.lastYear, self.lastMonth)		
        self.disney_link = 'http://www.imdb.com/search/title?companies=disney&title_type=feature,tv_movie&start=1'
        self.top250_link = 'http://www.imdb.com/search/title?groups=top_250&title_type=feature,tv_movie'
				
		
		
        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api.trakt.tv/users/me/collection/movies'
        self.traktwatchlist_link = 'http://api.trakt.tv/users/me/watchlist/movies'
        self.traktfeatured_link = 'http://api.trakt.tv/recommendations/movies?limit=40'
        self.trakthistory_link = 'http://api.trakt.tv/users/me/history/movies?limit=40&page=1'
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?sort=list_order,asc&st_dt=&mode=detail&page=1'
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&title_type=feature,short,tv_movie,tv_special,video,documentary,game&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user

        self.tmdbdvd_link = 'https://api.themoviedb.org/3/discover/movie?api_key=%s&language=en-US&sort_by=popularity.desc&certification_country=US&include_adult=false&include_video=false&page=1&primary_release_date.gte=%s&primary_release_date.lte=%s&vote_count.gte=20&with_release_type=5' % ("%s", self.last180days, self.Today)

        self.imdbsearch_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&title=%s&start=1'
		
		
    def getSearch(self, title=None):
        try:
            if (title == None or title == ''): return
            url = self.imdbsearch_link % title
            self.list = cache.get(self.imdb_list, 720, url)
            self.list = [i for i in self.list if cleantitle.get(title) == cleantitle.get(i['title'])]
            self.worker()
            return self.list
        except:
            pass
			
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
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass
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
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                if idx == True: self.worker()

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()

            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_userlist, 0, url)
                if idx == True: self.worker()

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                if idx == True: self.worker()

            elif u in self.tmdb_link:
                self.list = cache.get(self.tmdb_list, 24, url)
                self.workerTMDB()


            if idx == True and create_directory == True: self.movieDirectory(self.list)
            return self.list
        except:
            pass

			
			
			
			
			
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
            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            title = k.getText() if k.isConfirmed() else None
            if (title == None or title == ''): return

            url = self.imdbsearch_link % title
            self.get(url)
            
        except:
            pass


    def person(self):
        try:
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = self.persons_link + urllib.quote_plus(q)
            url = '%s?action=moviePersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            control.execute('Container.Update(%s)' % url)
        except:
            return


    def genres(self):
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
                'image': 'genres.png',
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

        for i in languages: self.list.append({'name': str(i[0]), 'url': self.language_link % i[1], 'image': 'languages.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list


    def certifications(self):
        certificates = ['G', 'PG', 'PG-13', 'R', 'NC-17']

        for i in certificates: self.list.append({'name': str(i), 'url': self.certification_link % str(i).replace('-', '_').lower(), 'image': 'certificates.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list


    def years(self):
        year = (self.datetime.strftime('%Y'))

        for i in range(int(year)-0, 1900, -1): self.list.append({'name': str(i), 'url': self.year_link % (str(i), str(i)), 'image': 'years.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list


    def persons(self, url):
        if url == None:
            self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        else:
            self.list = cache.get(self.imdb_person_list, 1, url)

        for i in range(0, len(self.list)): self.list[i].update({'action': 'movies'})
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

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'movies'})
        self.addDirectory(self.list, queue=True)
        return self.list


    def trakt_list(self, url, user):
        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

            result = trakt.getTraktAsJson(u)

            items = []
            for i in result:
                try: items.append(i['movie'])
                except: pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            if not int(q['limit']) == len(items): raise Exception()
            q.update({'page': str(int(q['page']) + 1)})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['title']
                title = client.replaceHTMLCodes(title)

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                tmdb = str(item.get('ids', {}).get('tmdb', 0))
				
				# METALIBRARY
                self.remotedbMeta = self.remotedb_meta(imdb=imdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image +  meta['fanart']})
					self.list.append(meta)
					raise Exception()

                try: premiered = item['released']
                except: premiered = '0'
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'

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

                try: tagline = item['tagline']
                except: tagline = '0'
                if tagline == None: tagline = '0'
                tagline = client.replaceHTMLCodes(tagline)

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'tagline': tagline, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': '0', 'fanart': '0', 'next': next})
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

                try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except: url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list

		
		
    def tmdb_list(self, url):
        result = tmdbapi.request(url)
        result = json.loads(result)
        items = result['results']
		
        for item in items:
            try:
                page = result.get('page')
                next = int(page) + 1
                nextPage = 'page=%s' % str(next)
                currPage = re.findall('page=(\d+)', url)[0]

                next = url.replace('page=%s' % currPage, nextPage)
				
                title = item['title']
                title = title.encode('utf-8')

                year = item['release_date']
                try: year = re.compile('(\d{4})').findall(str(year))[0]
                except: year = '0'
                year = year.encode('utf-8')
				
                tmdb = item.get('id')
                tmdb = str(tmdb)
				
				# METALIBRARY
                self.remotedbMeta = self.remotedb_meta(tmdb=tmdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image +  meta['fanart']})
					self.list.append(meta)
					raise Exception()
					
				
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'tmdb': tmdb, 'tvdb': '0', 'next': next})
            except:
                pass

        return self.list
		

    def imdb_list(self, url):
        try:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            def imdb_watchlist_id(url):
                return client.parseDOM(requests.get(url).content, 'meta', ret='content', attrs = {'property': 'pageId'})[0]

            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url

            elif url == self.imdbwatchlist2_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist2_link % url

            result = requests.get(url).content

            result = result.replace('\n', ' ')

            items = client.parseDOM(result, 'div', attrs = {'class': 'lister-item mode-advanced'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
			
            
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:


                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]
                imdb = imdb.encode('utf-8')
				
				# METALIBRARY
                self.remotedbMeta = self.remotedb_meta(imdb=imdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image +  meta['fanart']})
					self.list.append(meta)
					raise Exception()
					
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})

                year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
                try: year = re.compile('(\d{4})').findall(str(year))[0]
                except: year = '0'
                year = year.encode('utf-8')

                # if int(year) > int((self.datetime).strftime('%Y')): raise Exception()


                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})[0]
                except: genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = re.findall('(\d+?) min(?:s|)', item)[-1]
                except: duration = '0'
                duration = duration.encode('utf-8')

                rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: pass
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                except: pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
                except: votes = '0'
                try: votes = re.findall('\((.+?) vote(?:s|)\)', votes)[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                try: director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: director = '0'
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                plot = '0'
                try: 
					plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
					try:
						plot = re.findall('([^<]+)', plot)[0]
						plot = ' '.join(plot.split())
					except:pass
                except: pass
                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                plot = re.sub('<.+?>|</.+?>', '', plot)
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'plot': plot, 'tagline': '0', 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return self.list

    def imdb_userlist(self, url):
        try:

            result = requests.get(url).content
            result = result.replace('\n', ' ')
            items = client.parseDOM(result, 'div', attrs = {'class': 'lister-item mode-detail'})
        except:
            return

        try:
            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': '.+?next-page'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
			
                imdb = re.findall('data-tconst="(tt\d*)"', item)[0]
                imdb = imdb.encode('utf-8')
				
				
				# METALIBRARY
                self.remotedbMeta = self.remotedb_meta(imdb=imdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image +  meta['fanart']})
					self.list.append(meta)
					raise Exception()
					
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})

                year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
                try: year = re.compile('(\d{4})').findall(str(year))[0]
                except: year = '0'
                year = year.encode('utf-8')

                # if int(year) > int((self.datetime).strftime('%Y')): raise Exception()


                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})[0]
                except: genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = re.findall('(\d+?) min(?:s|)', item)[-1]
                except: duration = '0'
                duration = duration.encode('utf-8')

                rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: pass
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                except: pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
                except: votes = '0'
                try: votes = re.findall('\((.+?) vote(?:s|)\)', votes)[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                try: director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: director = '0'
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                plot = '0'
                plot = re.findall('<p class="">(.+?)<', item)[0]

                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'plot': plot, 'tagline': '0', 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return self.list

    def imdb_person_list(self, url):
        try:
            result = requests.get(url).content
            items = client.parseDOM(result, 'tr', attrs = {'class': '.+? detailed'})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, 'a', ret='title')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = client.parseDOM(item, 'img', ret='src')[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

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
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url.split('/list/', 1)[-1].replace('/', '')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k['name']))
        return self.list
		
    def inProgress(self):
        from resources.lib.modules import favourites
        try:
            items = favourites.getProgress('movies')
            self.list = [i[1] for i in items]

            for i in self.list:
                if not 'name' in i: i['name'] = '%s (%s)' % (i['title'], i['year'])
                try: i['title'] = i['title'].encode('utf-8')
                except: pass
                try: i['name'] = i['name'].encode('utf-8')
                except: pass
                if not 'duration' in i: i['duration'] = '0'
                if not 'imdb' in i: i['imdb'] = '0'
                if not 'tmdb' in i: i['tmdb'] = '0'
                if not 'poster' in i: i['poster'] = '0'
                if not 'banner' in i: i['banner'] = '0'
                if not 'fanart' in i: i['fanart'] = '0'
				

            self.worker()
            
            self.movieDirectory(self.list)
        except:
            return
			
    def favourites(self):
        try:
            items = favourites.getFavourites('movies')
            self.list = [i[1] for i in items]

            for i in self.list:
                if not 'name' in i: i['name'] = '%s (%s)' % (i['title'], i['year'])
                try: i['title'] = i['title'].encode('utf-8')
                except: pass
                try: i['name'] = i['name'].encode('utf-8')
                except: pass
                if not 'duration' in i: i['duration'] = '0'
                if not 'imdb' in i: i['imdb'] = '0'
                if not 'tmdb' in i: i['tmdb'] = '0'
                if not 'tvdb' in i: i['tvdb'] = '0'
                if not 'tvrage' in i: i['tvrage'] = '0'
                if not 'poster' in i: i['poster'] = '0'
                if not 'banner' in i: i['banner'] = '0'
                if not 'fanart' in i: i['fanart'] = '0'
				

            self.worker()
            self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))	           
            self.movieDirectory(self.list)
        except:
            return


    def worker(self, level=1):
        self.meta = []
        total = len(self.list)

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total: threads.append(libThread.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if not i['imdb'] == '0']

    def workerTMDB(self, level=1):
        self.meta = []
        total = len(self.list)

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total: threads.append(libThread.Thread(self.super_infoTMDB, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if not i['imdb'] == '0']

        # self.list = metacache.local(self.list, self.tm_img_link, 'poster3', 'fanart2')

        if self.fanart_tv_user == '':
            for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})
			

    def super_infoTMDB(self, i):
        try:

            if self.list[i]['metacache'] == True: raise Exception()
			
            if 'metalibrary' in self.list[i]:
				print ("USING REMOTEDB META MOVIES")
				metaDict = {'imdb': self.list[i]['imdb'], 'tmdb': self.list[i]['tmdb'], 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
				self.meta.append(metaDict)
				if self.list[i]['metalibrary'] == True: raise Exception()
				
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
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
		
            if tmdb == '0': raise Exception()
            details = tmdbapi.getDetails(tmdb)
			
                # if int(year) > int((self.datetime).strftime('%Y')): raise Exception()
            imdb = details['imdb_id']
            if imdb == '' or imdb == None or imdb == '0': raise Exception()

            poster = details['poster_path']
            if not poster == '' or poster == '0' or poster == None: poster = self.tmdb_poster + poster
            fanart = details['backdrop_path']
            if not fanart == '' or fanart == '0' or fanart == None: fanart = self.tmdb_image + fanart

            try:
				genres = details['genres']
				genre = [x['name'] for x in genres]
				genre = ' / '.join(genre)
            except: genre = '0'

            try: duration = details.get('runtime')
            except: duration = '0'
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
				director = director.encode('utf-8')
            except: director = '0'

				
            plot = details['overview']
            if plot == '' or plot == None: plot = '0'
            plot = plot.encode('utf-8')
			
            tagline = details['tagline']
            if tagline == '' or tagline == tagline: tagline = '0'
            tagline = tagline.encode('utf-8')
			
	
            item = {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster, 'poster2': poster, 'poster3': poster, 'banner': banner, 'fanart': fanart, 'fanart2': fanart, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'plot': plot, 'tagline': tagline}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)
            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass
			
    def remotedb_meta(self, imdb=None, tmdb=None):
		try:
			dbmeta = metalibrary.metaMovies(imdb=imdb, tmdb=tmdb)
			return dbmeta
            
		except:pass
				

    def super_info(self, i):
        try:
            if self.list[i]['metacache'] == True: raise Exception()
			
            if 'metalibrary' in self.list[i]:
				print ("USING REMOTEDB META MOVIES")
				metaDict = {'imdb': self.list[i]['imdb'], 'tmdb': self.list[i]['tmdb'], 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': self.list[i]}
				self.meta.append(metaDict)
				if self.list[i]['metalibrary'] == True: raise Exception()
				
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
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'

            artmeta = True
            poster2 = '0'
            poster3 = '0'
            fanart2 = '0'
            clearlogo = '0'
            clearart = '0'
            banner = '0'
			
            metaDB = False	
			
            if fanart == '0' or fanart == '' or fanart == None or poster == '' or poster == None or poster == '0': 
				tmdbArt = tmdbapi.getImdb(imdb)
				try: 
					tmdbArt = json.loads(tmdbArt)
					tmdbArt = tmdbArt['movie_results'][0]
				except: artmeta = False
				

				
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
					poster2 = poster2.encode('utf-8')
					if "http" in poster2: poster = poster2
				except:
					poster2 = '0'

				try:
					fanart = tmdbArt['backdrop_path']
					if fanart == '' or fanart == None: fanart = '0'
					if not fanart == '0': fanart = self.tmdb_image + fanart
					fanart = fanart.encode('utf-8')
				except:
					fanart = '0'	

            if fanart == '0' or fanart == '' or fanart == None or poster == '' or poster == None or poster == '0': 
				ftvmeta = fanarttv.get(imdb, 'movies')
				poster3 = ftvmeta['poster']
				if poster == '' or poster == '0' or poster == None: poster = poster3
				fanart = ftvmeta['fanart']
				banner = ftvmeta['banner']

            try:
                
                if self.lang == 'en': raise Exception()

                item = trakt.getMovieSummary(imdb)				
                if self.lang not in item.get('available_translations', [self.lang]): raise Exception()
                trans_item = trakt.getMovieTranslation(imdb, self.lang, full=True)
  
                title = trans_item.get('title') or title
                tagline = trans_item.get('tagline') or tagline
                plot = trans_item.get('overview') or plot
            except:
                pass

            if "http" in poster: artmeta = True 
            if "http" in fanart: artmeta = True	


            if duration == '0' or duration == None or duration == '': duration = '120'
            else: duration = str(int(duration) * 60)
				
            item = {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster, 'poster2': poster, 'poster3': poster, 'banner': banner, 'fanart': fanart, 'fanart2': fanart, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'plot': plot, 'tagline': tagline}


            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getMovieIndicators(refresh=True) if action == 'movies' else playcount.getMovieIndicators()

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')


        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')
		
        remoteManagerMenu = 'Remote Library'

        nextMenu = control.lang(32053).encode('utf-8')
		
        addToWatchlist = control.lang(40010).encode('utf-8')
        removeFromWatchlist = control.lang(40011).encode('utf-8')
				
        removeFromProgress = control.lang(40012).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')
		
        for i in items:
            try:
                label = '%s' % (i['title'])

                imdb, tmdb, title, year = i['imdb'], i['tmdb'], i['originaltitle'], i['year']
				
                # try:
					# ratio = premiumize.check_cloud(label) 
					# label = "[COLOR lime][CLOUD " + ratio + "][/COLOR] " + label
                # except:pass
				
                sysname = urllib.quote_plus('%s (%s)' % (title, year))
                bookmarkname = urllib.unquote_plus(sysname)
                systitle = urllib.quote_plus(title)

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tmdb_id': tmdb})
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                #meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not 'duration' in i: meta.update({'duration': '120'})
                elif i['duration'] == '0': meta.update({'duration': '120'})
                try: meta.update({'duration': str(int(meta['duration']))})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                poster = i['poster']
                if poster == '' or poster == '0' or poster == None: poster = addonPoster
                
                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, sysmeta)
                sysurl = urllib.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)
                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
                
                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                if control.setting('remotedb.list') == 'true': cm.append((remoteManagerMenu, 'RunPlugin(%s?action=remoteManager&imdb=%s&tmdb=%s&meta=%s&content=movie)' % (sysaddon, imdb, tmdb, sysmeta)))

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (sysaddon, sysname, imdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))
					
                if not action == 'movieFavourites':cm.append((addToWatchlist, 'RunPlugin(%s?action=addFavourite&meta=%s&content=movies)' % (sysaddon, sysmeta)))
                if action == 'movieFavourites': cm.append((removeFromWatchlist, 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=movies)' % (sysaddon, sysmeta)))
                if action == 'moviesInProgress': cm.append((removeFromProgress, 'RunPlugin(%s?action=deleteProgress&meta=%s&content=movies)' % (sysaddon, sysmeta)))

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

                item.setArt(art)
               			
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
				
                played = bookmarks.bookmarks().get(bookmarkname.lower())
                item.setProperty('resumetime', played)

                item.setInfo(type='Video', infoLabels = meta)
               
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=moviePage&url=%s' % (sysaddon, urllib.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)

    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                cm = []

                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=movie&url=%s)' % (sysaddon, urllib.quote_plus(i['url']))))

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try: cm.append((addToLibrary, 'RunPlugin(%s?action=moviesToLibrary&url=%s)' % (sysaddon, urllib.quote_plus(i['context']))))
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
