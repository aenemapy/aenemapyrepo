# -*- coding: utf-8 -*-

from resources.lib.api import trakt
from resources.lib.modules import cleantitle
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import utils
from resources.lib.api import tvdbapi, tmdbapi, fanarttv
from resources.lib.modules import favourites
import os,sys,re,json,urllib,urlparse,datetime
import metalibrary
import libThread
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

import requests


class tvshows:
    def __init__(self):
        self.list = []

        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api.trakt.tv'
        self.tvmaze_link = 'http://www.tvmaze.com'
        self.tvdb_key = control.setting('tvdb.api')
        if self.tvdb_key == '' or self.tvdb_key == '0' or self.tvdb_key == None: self.tvdb_key = '69F2FCC839393569'
		
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
		
        
        self.user = 'realizer'
        self.lang = control.apiLanguage()['tvdb']

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
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=tv_series,mini_series&start=1'
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&sort=created:desc&title_type=tv_series,mini_series&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user

		
		########### TVDB API 2 #######################		
        self.tvdb2_api = 'https://api.thetvdb.com'
        self.tvdb2_info_series = 'https://api.thetvdb.com/series/%s'
        self.tvdb2_series_poster = 'https://api.thetvdb.com/series/%s/images/query?keyType=poster'	% ('%s')
        self.tvdb2_series_fanart = 'https://api.thetvdb.com/series/%s/images/query?keyType=fanart'	% ('%s')
        self.tvdb2_series_banner = 'https://api.thetvdb.com/series/%s/images/query?keyType=series'	% ('%s')
        self.tvdb2_series_season = 'https://api.thetvdb.com/series/%s/images/query?keyType=season'	% ('%s')
        self.tvdb2_series_bannerseason = 'https://api.thetvdb.com/series/%s/images/query?keyType=seasonwide'	% ('%s')
        self.tvdb2_by_imdb = 'https://api.thetvdb.com/search/series?imdbId=%s'
        self.tvdb2_by_query = 'https://api.thetvdb.com/search/series?name=%s'
        self.tvdb2_series_actors = 'https://api.thetvdb.com/series/%s/actors'	% ('%s')		
				
    def getSearch(self, title = None):
        try:
            if (title == None or title == ''): return
            url = 'https://api.thetvdb.com/search/series?name=%s'  % (urllib.quote_plus(title))
            self.list = cache.get(self.getTvdb, 720, url, False)
            self.list = [i for i in self.list if cleantitle.get(title) == cleantitle.get(i['tvshowtitle'])]
            return self.list
        except:
            return			
		
    def get(self, url, idx=True, create_directory=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass


            if u in self.trakt_link and '/users/' in url:
                try:
                    if not '/users/me/' in url: raise Exception()
                    # if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
                    # self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                    self.list = self.trakt_list(url, self.trakt_user)
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
                self.list = cache.get(self.imdb_list, 0, url)
                if idx == True: self.worker()

            elif u in self.imdb_link:
                # self.list = cache.get(self.imdb_list, 24, url)
				
                self.list = self.imdb_list(url)
                if idx == True: self.worker()


            elif u in self.tvmaze_link:
                self.list = cache.get(self.tvmaze_list, 168, url)
                if idx == True: self.worker()


            if idx == True and create_directory == True: self.tvshowDirectory(self.list)
            return self.list
        except:
            pass

			
    def getTvdbFav(self, idx=True, create_directory=True):	
        url = '0'
        if control.setting('tvdb.cache') == 'true': self.list = cache.get(self.getTvdbList, 60, url, self.user)	
        else: self.list = self.getTvdbList(url, self.user)			
        try:self.worker()
        except:pass
        self.list = sorted(self.list, key=lambda k: utils.title_key(k['title']))
        self.tvshowDirectory(self.list)	

		
    def getTvdbList(self, url, user):
		self.list = []
		try:
			# print ("TVDB MY FAV")
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
						title = title.encode('utf-8')
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
						# print ("SEARCH TVDB plot", plot)				
						tmdb = '0'
						imdb = '0'
						
						self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': '0', 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': '0', 'banner': '0', 'fanart': '0', 'next': ''})
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

					try: title = item['seriesName']
					except: title = ''
					if title == '': title = '0'
					title = client.replaceHTMLCodes(title)
					title = title.encode('utf-8')
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
					try: 
						tvdb = item['id']
						tvdb = str(tvdb)
					except: tvdb = '0'
					
					# print ("SEARCH TVDB tvdb", tvdb)
					if tvdb == '': raise Exception()
					try: plot = item['overview']
					except: plot = ''
					if plot == '': plot = '0'
					plot = plot.encode('utf-8')
					# print ("SEARCH TVDB plot", plot)				
					tmdb = '0'
					imdb = '0'
					
					self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': '0', 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': '0', 'banner': '0', 'fanart': '0', 'next': ''})
				except:
					continue

			
			try:self.worker()
			except:pass

			if idx == True: self.tvshowDirectory(self.list)
			return self.list
		except:
			pass			
			


    def searchTvdb(self):
        try:
            #control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = 'https://api.thetvdb.com/search/series?name=%s'  % (urllib.quote_plus(q))
            self.getTvdb(url)
        except:
            return	
					
    def search(self):
        try:
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = self.search_link + urllib.quote_plus(q)
            self.get(url)
        except:
            return


    def person(self):
        try:
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = self.persons_link + urllib.quote_plus(q)
            url = '%s?action=tvPersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            self.persons(url)
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
                'image': 'genres.png',
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


    def persons(self, url):
        if url == None:
            self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        else:
            self.list = cache.get(self.imdb_person_list, 1, url)

        for i in range(0, len(self.list)): self.list[i].update({'action': 'tvshows'})
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
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def trakt_list(self, url, user):
        try:
            dupes = []

            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

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
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                self.remotedbMeta = self.remotedb_meta(imdb=imdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'tvshowtitle': meta['title'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image + meta['fanart']})
					self.list.append(meta)
					raise Exception()
						
				
                self.remotedbMeta = self.remotedb_meta(imdb=imdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'tvshowtitle': meta['title'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image + meta['fanart']})
					self.list.append(meta)
					raise Exception()
					

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

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'next': next})
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


    def imdb_list(self, url):
        try:
            dupes = []

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
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'tvshowtitle': meta['title'], 'originaltitle': meta['title'], 'next': next, 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image + meta['fanart']})
					self.list.append(meta)
					raise Exception()
					
					
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
                year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
                year = re.findall('(\d{4})', year[0])[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()



                if imdb in dupes: raise Exception()
                dupes.append(imdb)

                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

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

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'rating': rating, 'plot': plot, 'votes': votes, 'imdb': imdb, 'tvdb': '0', 'poster': poster, 'next': next})
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
            items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'})
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


    def tvmaze_list(self, url):
        try:
            result = requests.get(url).content
            result = client.parseDOM(result, 'section', attrs = {'id': 'this-seasons-shows'})

            items = client.parseDOM(result, 'li')
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
                title = title.encode('utf-8')

                year = item['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['externals']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['externals']['thetvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                if tvdb == None or tvdb == '': raise Exception()
 
                try: poster = item['image']['original']
                except: poster = '0'
                if poster == None or poster == '': poster = '0'
                poster = poster.encode('utf-8')

                premiered = item['premiered']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['network']['name']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try: duration = item['runtime']
                except: duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration.encode('utf-8')

                try: rating = item['rating']['average']
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating.encode('utf-8')

                try: plot = item['summary']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                try: content = item['type'].lower()
                except: content = '0'
                if content == None or content == '': content = '0'
                content = content.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'content': content})
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


    def worker(self, level=1):
        self.meta = []
        total = len(self.list)

        self.fanart_tv_headers = {'api-key': 'b1159fd31a9a841afe8102fd6c2e3cfc' }
        if not self.fanart_tv_user == '':
            self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total: threads.append(libThread.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if i['tvdb'] != '0' and i['tvdb'] != '' and i['tvdb'] != None]

		
    def remotedb_meta(self, imdb=None, tmdb=None, tvdb=None):
		try:
			dbmeta = metalibrary.metaTV(imdb=imdb, tmdb=tmdb, tvdb=tvdb)
			return dbmeta
            
		except:pass

    def super_info(self, i):
        try:
		
            
            if self.list[i]['metacache'] == True: raise Exception()

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
                    imdb = trakt.SearchTVShow(urllib.quote_plus(self.list[i]['title']), self.list[i]['year'], full=False)[0]
                    imdb = imdb.get('show', '0')
                    imdb = imdb.get('ids', {}).get('imdb', '0')
                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

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
					tvdb = tvdb.encode('utf-8')
				
				else:
					url = self.tvdb2_by_query % (urllib.quote_plus(self.list[i]['title']))
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
					
            # print ("FANART TV ART 1", self.fanart_tv_user)
            if tvdb == '' or tvdb == None or tvdb == '0': raise Exception()
            clearlogo = '0'
            clearart = '0'	
            banner = '0'		
			
            try: 
                self.remotedbMeta = self.remotedb_meta(imdb=imdb, tvdb=tvdb)
                if len(self.remotedbMeta) > 0: 
					meta = self.remotedbMeta
					meta.update({'metalibrary': True, 'year': meta['premiered'], 'tvshowtitle': meta['title'], 'originaltitle': meta['title'], 'poster': self.tmdb_poster + meta['poster'], 'fanart': self.tmdb_image + meta['fanart']})
					self.list[i].update(meta)
					return
            except: pass
			
            metaDB = False	


			

            if poster == '' or poster =='0' or poster == None or fanart == '' or fanart =='0' or fanart == None:
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
						poster = poster.encode('utf-8')
				except:
					pass
				try:
					if fanart == '0' or fanart == '' or fanart == None:
						fanart = tmdbArt['backdrop_path']
						fanart = self.tmdb_image + fanart
						fanart = fanart.encode('utf-8')
				except:
					fanart = '0'	

            if poster == '' or poster =='0' or poster == None: poster = tvdbapi.getPoster(tvdb)	
            if fanart == '' or fanart =='0' or fanart == None: fanart = tvdbapi.getFanart(tvdb)	
            # if banner == '' or banner =='0' or banner == None: banner = tvdbapi.getBanner(tvdb)	
			
            if poster == '' or poster =='0' or poster == None or fanart == '' or fanart =='0' or fanart == None:
				ftvmeta = fanarttv.get(tvdb, 'tv')
				poster3 = ftvmeta['fanart']
				if poster == '' or poster == '0' or poster == None: poster = poster3
				if fanart == '' or fanart == '0' or fanart == None: fanart = ftvmeta['fanart']
				banner = ftvmeta['banner']			
			
            try:
				if self.lang == 'en': raise Exception()
				trans_item = tvdbapi.getTvdbTranslation(tvdb)
				trans = json.loads(trans_item)
				title = trans['data']['seriesName']
				plot = trans['data']['overview']
            except:
                pass			
            if "http" in poster: artmeta = True 
            elif "http" in fanart: artmeta = True
			
            item = {'title': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)
            if artmeta == False: raise Exception()
	
            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass
			
			
			

			
    def favourites(self):
        try:
            items = favourites.getFavourites('tvshows')
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
                if not 'clearart' in i: i['clearart'] = '0'
                if not 'clearlogo' in i: i['clearlogo'] = '0'
                i['originaltitle'] = i['title'].encode('utf-8')
																			

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

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        indicators = playcount.getTVShowIndicators(refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

        flatten = True if control.setting('flatten.tvshows') == 'true' else False

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        nextMenu = control.lang(32053).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')
		
        addToWatchlist = control.lang(40010).encode('utf-8')
        removeFromWatchlist = control.lang(40011).encode('utf-8')
					
        remoteManagerMenu = 'Remote Library'
		
        for i in items:
            try:
                label = i['title']

                systitle = sysname = urllib.quote_plus(i['originaltitle'])
                sysimage = urllib.quote_plus(i['poster'])
                imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']
				
                # try:
					# ratio = premiumize.check_cloud(label) 
					# label = "[COLOR lime][CLOUD " + ratio + "][/COLOR] " + label
                # except:pass			
				

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tvdb_id': tvdb})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(label))})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass


                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, sysmeta)

                cm = []
                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tvdb))
                    if overlay == 7: 
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&query=6)' % (sysaddon, systitle, imdb, tvdb)))
						meta.update({'playcount': 1, 'overlay': 7})
                    else: 
						cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=0&query=7)' % (sysaddon, systitle, imdb, tvdb)))
						meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass


                if control.setting('remotedb.list') == 'true': cm.append((remoteManagerMenu, 'RunPlugin(%s?action=remoteManager&imdb=%s&tvdb=%s&meta=%s&content=tv)' % (sysaddon, imdb, tvdb, sysmeta)))

                if not action == 'tvFavourites':cm.append((addToWatchlist, 'RunPlugin(%s?action=addFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))
                if action == 'tvFavourites': cm.append((removeFromWatchlist, 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))

                # if not action == 'tvdbFav':cm.append(('Add To Tvdb', 'RunPlugin(%s?action=tvdbAdd&tvshowtitle=%s&tvdb=%s)' % (sysaddon, systitle, tvdb)))
                # if action == 'tvdbFav': cm.append(('Remove From Tvdb', 'RunPlugin(%s?action=tvdbRemove&tvdb=%s)' % (sysaddon, tvdb)))
				
                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

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

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=tvshowPage&url=%s' % (sysaddon, urllib.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'tvshows')
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

                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=show&url=%s)' % (sysaddon, urllib.quote_plus(i['url']))))

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try: cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowsToLibrary&url=%s)' % (sysaddon, urllib.quote_plus(i['context']))))
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


