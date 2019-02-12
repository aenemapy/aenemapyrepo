# -*- coding: utf-8 -*-

from resources.lib.api import trakt
from resources.lib.modules import cleantitle
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import playcount
from resources.lib.modules import views
from resources.lib.modules import utils
from resources.lib.modules import bookmarks

from resources.lib.api import tvdbapi
import libThread
import os,sys,re,json,zipfile,StringIO,urllib,urllib2,urlparse,datetime,json,time

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()

action = params.get('action')

control.moderator()


class seasons:
    def __init__(self):
        self.list = []
        self.poster = ''
        self.fanart = ''
        self.seasons_posters = '0'
        self.episodeLibrary = []
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
        self.tvdb2_episodes = 'https://api.thetvdb.com/series/%s/episodes'	% ('%s')	
        self.tvdb2_get_episode = 'https://api.thetvdb.com/episodes/%s'

		
		
				
		
		

    def get(self, tvshowtitle, year, imdb, tvdb, idx=True, create_directory=True):
        if control.window.getProperty('PseudoTVRunning') == 'True':
            return episodes().get(tvshowtitle, year, imdb, tvdb)

        if idx == True:
            self.list = cache.get(self.tvdb_list, 24, tvshowtitle, year, imdb, tvdb, '')
            if create_directory == True: self.seasonDirectory(self.list)
            return self.list
        else:
            self.list = self.tvdb_list(tvshowtitle, year, imdb, tvdb, 'en')
            return self.list


    def tvdb_list(self, tvshowtitle, year, imdb, tvdb, lang, limit='', season=None, episode=None):

        try:
            if imdb == '0':
                try:
                    imdb = trakt.SearchTVShow(urllib.quote_plus(tvshowtitle), year, full=False)[0]
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
				try:	tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(item))[0]
				except: tvdb = ''
				if tvdb == '': tvdb = '0'
				tvdb = tvdb.encode('utf-8')

            if tvdb == '0':
                url = self.tvdb2_by_query % (urllib.quote_plus(self.list[i]['title']))
                result = tvdbapi.getTvdb(url)
                item = json.loads(result)
                item = item['data']
                years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]
                tvdb = [(x, x['seriesName'], x['firstAired']) for x in item]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1]) and any(y in x[2] for y in years)]
                tvdb = [x[0] for x in tvdb][0]
                try:	tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(tvdb))[0]
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
			
            label = tvshowtitle
            year = year
            tvdb = tvdb
            imdb = imdb
            poster = '0'

            banner = '0'
            cast = '0'
			
            self.poster = '0'
            self.fanart = '0'
            self.seasons_posters = '0'

            getmeta = []


            getmeta.append(libThread.Thread(self.threadPoster,tvdb))
            getmeta.append(libThread.Thread(self.threadFanart,tvdb))
            getmeta.append(libThread.Thread(self.threadSeasons,tvdb))			
            [i.start() for i in getmeta]	
            [i.join() for i in getmeta]	
            for i in range(0,30):
				try:
					time.sleep(0.5)
					is_alive = [x for x in getmeta if x.is_alive() == True]
					if not is_alive: break
				except:
					pass
            poster = self.poster
            fanart = self.fanart
	
            try: premiered = api['firstAired'].encode('utf-8')
            except: premiered = '0'
            if premiered == '': premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = premiered.encode('utf-8')

            try: studio = api['network']
            except: studio = ''
            if studio == '': studio = '0'
            studio = client.replaceHTMLCodes(studio)
            studio = studio.encode('utf-8')

            try: genre = api['genre']
            except: genre = ''
            genre = [x for x in genre]
            genre = ' / '.join(genre)
            if genre == '': genre = '0'
            genre = client.replaceHTMLCodes(genre)
            genre = genre.encode('utf-8')

			
            try: duration = api['runtime']
            except: duration = ''
            if duration == '': duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = duration.encode('utf-8')			
            # print ("TVDB EPISODES duration", duration)	

            try: status = api['status']
            except: status = ''
            if status == '': status = '0'
            status = client.replaceHTMLCodes(status)
            status = status.encode('utf-8')

            try: rating = api.get('siteRating')
            except: rating = ''

            rating = str(rating)
            if rating == '': rating = '0'
            rating = rating.encode('utf-8')

            try: votes = api.get('siteRatingCount')
            except: votes = ''
            if votes == '' or votes == None: votes = '0'
				# print ("TVDB votes", votes)
				
            try: mpaa = api['rating']
            except: mpaa = ''
            if mpaa == '': mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = mpaa.encode('utf-8')

            cast = '0'
			
            try: plot = api['overview']
            except: plot = '0'
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
		
            episodes = []
		
            if limit == '':
				tvdb_Api = self.tvdb2_episodes % tvdb		
				result2 = tvdbapi.getTvdb(tvdb_Api)
				tvdb_req = json.loads(result2)
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
							
				seasons = [i for i in tvdb_data if str(i['airedEpisodeNumber']) == '1' and not str(i['airedSeason']) == '0']
				seasons = sorted(seasons, key = lambda x : x['airedSeason'])
			

            threadSeason = []		
            seasonList = []
            if limit == '':  episodes = []
            else:
				if limit == 'nextepisode':
					tvdb_Api = self.tvdb2_episodes % tvdb
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
					episodes = 	seasonList	
					seasons = []
				
				else:
					tvdb_Api = "https://api.thetvdb.com/series/%s/episodes/query?airedSeason=%s" % (tvdb, str(limit))
					json_tvdb = tvdbapi.getTvdb(tvdb_Api)
					tvdb_req = json.loads(json_tvdb)
					lastPage = tvdb_req['links']['last']
					tvdb_data = tvdb_req['data']

					if int(lastPage) > 1:
						for i in range(1, int(lastPage)+1):
							if i != 1: 
								nextPage = "?page=%s" % i
								nextPage = tvdb_Api + nextPage
								json_tvdb = tvdbapi.getTvdb(nextPage)
								tvdb_req  = json.loads(json_tvdb)
								tvdb_data += tvdb_req['data']	
								
					episodes = sorted(tvdb_data, key = lambda x : int(x['airedEpisodeNumber']))	
					seasons = []
				
        except:
            pass
	
			
        if limit == '':
			try: seasons_posters = self.seasons_posters
			except: seasons_posters = '0'
        for item in seasons:

            try:
                try: premiered = item['firstAired'].encode('utf-8')
                except: premiered = '0'
                if premiered == '': premiered = '0'
                premiered = client.replaceHTMLCodes(premiered)
                premiered = premiered.encode('utf-8')

                season = item.get('airedSeason')
                season = str(season)
                season = season.encode('utf-8')
                if season == '0': continue

                if not seasons_posters == '0':
					
					for thumbs, sid in seasons_posters:
						if sid.encode('utf-8') == season:
							thumb = thumbs.encode('utf-8')
							thumb = self.tvdb_image + thumb
							
                else: thumb = poster
			
                if thumb == '0' or thumb == '' or thumb == None: thumb = poster			

                self.list.append({'season': season, 'tvshowtitle': tvshowtitle, 'label': label, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': '0', 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb})
            except:
                pass

        threads = []
        episodelist = []

        for item in episodes:
			
            try:
                id = item.get('id')
                id = str(id)
                id = id.encode('utf-8')

                epnumber = item.get('airedEpisodeNumber')
                epnumber = str(epnumber)
                epnumber = epnumber.encode('utf-8')

                season = item.get('airedSeason')
                season = str(season)
                season = season.encode('utf-8')
                episodelist.append(id)

                try:title = item['episodeName'].encode('utf-8')
                except: title = '0'	

                try:premiered = item['firstAired'].encode('utf-8')
                except: premiered = '0'			
				
                if limit == 'nextepisode':
					if int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str(self.today_date))): continue  
					
                self.list.append({'id': id, 'epnumber' : epnumber, 'title': title,'label': title, 'season': season, 'episode': epnumber, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': '0', 'fanart': fanart, 'thumb': fanart})

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
        # print ("premiumizer FINAL LISTS", self.list)
        return self.list
		

		
    def tvdbLibrary(self, tvshowtitle, year, imdb, tvdb, lang, limit=''):

        try:
            if imdb == '0':
                try:
                    imdb = trakt.SearchTVShow(urllib.quote_plus(tvshowtitle), year, full=False)[0]
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
				try:	tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(item))[0]
				except: tvdb = ''
				if tvdb == '': tvdb = '0'
				tvdb = tvdb.encode('utf-8')

            if tvdb == '0':
                url = self.tvdb2_by_query % (urllib.quote_plus(self.list[i]['title']))
                result = tvdbapi.getTvdb(url)
                item = json.loads(result)
                item = item['data']
                years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]
                tvdb = [(x, x['seriesName'], x['firstAired']) for x in item]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1]) and any(y in x[2] for y in years)]
                tvdb = [x[0] for x in tvdb][0]
                try:	tvdb = re.findall('''['"]id['"]:\s*(\d+)''', str(tvdb))[0]
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

            tvdbApi = self.tvdb2_episodes % tvdb		
            result2 = tvdbapi.getTvdb(tvdbApi)
            tvdbApi = json.loads(result2)
            tvdbApi = tvdbApi['data']
				
		
            episodes = []
            seasons = [i for i in tvdbApi if str(i['airedEpisodeNumber']) == '1' and not str(i['airedSeason']) == '0']
            seasons = sorted(seasons, key = lambda x : x['airedSeason'])
			
            # episodes = [i for i in tvdbApi]			
            # episodes = sorted(episodes, key = lambda x : x['airedSeason'])
            threadSeason = []		

            
            for item in seasons:
				try:
						season = item.get('airedSeason')
						season = str(season)
						season = season.encode('utf-8')
						if season == '0': continue
						url = "https://api.thetvdb.com/series/%s/episodes/query?airedSeason=%s" % (tvdb, str(season))
						threadSeason.append(libThread.Thread(self.threadEpisodes, url))	
				except:
						pass
                					
            [i.start() for i in threadSeason]
            [i.join() for i in threadSeason]							
            episodes = []
            seasons = []



        except:
            pass
	
			

        for item in self.episodeLibrary:
			
            try:
                id = item.get('id')
                id = str(id)
                id = id.encode('utf-8')
				
                epnumber = item.get('airedEpisodeNumber')
                epnumber = str(epnumber)
                epnumber = epnumber.encode('utf-8')

                season = item.get('airedSeason')
                season = str(season)
                season = season.encode('utf-8')

                try:title = item['episodeName'].encode('utf-8')
                except: title = '0'	

                try:premiered = item['firstAired'].encode('utf-8')
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
			self.episodeLibrary += r
			return self.episodeLibrary
			
			
			
        except:
            pass
	

    def threadPoster(self, tvdb):
        try:
			
			self.poster = tvdbapi.getPoster(tvdb)
			# print ("premiumizer META POSTER", self.poster)
			return self.poster

        except:
            pass
	
	
    def threadFanart(self, tvdb):
        try:
			self.fanart = tvdbapi.getFanart(tvdb)
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
            try:thumb = item['filename'].encode('utf-8')
            except: thumb = '0'
            if thumb == '': thumb = '0'
            if not thumb == '0': 
				thumb = self.tvdb_image + thumb
				self.list[i].update({'thumb': thumb})
				


            try:title = item['episodeName'].encode('utf-8')
            except: title = '0'
            if title == '': title = '0'
            if not title == '0': 
				self.list[i].update({'title': title})
				self.list[i].update({'label': title})
				
            try:plot = item['overview'].encode('utf-8')
            except: plot = '0'
            if plot == '': plot = '0'
            if not plot == '0': 
				self.list[i].update({'plot': plot})
				
            try:plot = item['overview'].encode('utf-8')
            except: plot = '0'
            if plot == '': plot = '0'
            if not plot == '0': 
				self.list[i].update({'plot': plot})


            try:premiered = item['firstAired'].encode('utf-8')
            except: premiered = '0'
            if premiered == '': premiered = '0'
            if not premiered == '0': 
				self.list[i].update({'premiered': premiered})
			
            try: rating = item.get('siteRating')
            except: rating = ''
            rating = str(rating)
            if rating == '': rating = '0'
            rating = rating.encode('utf-8')
            if not rating == '0': 
				self.list[i].update({'rating': rating})
						

            try: votes = item.get('siteRatingCount')
            except: votes = ''
            if votes == '' or votes == None: votes = '0'
            if not votes == '0': 
				self.list[i].update({'votes': votes})

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

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        labelMenu = control.lang(32055).encode('utf-8')

        playRandom = control.lang(32535).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                label = '%s %s' % (labelMenu, i['season'])
                systitle = sysname = urllib.quote_plus(i['tvshowtitle'])

                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"
                imdb, tvdb, year, season = i['imdb'], i['tvdb'], i['year'], i['season']

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
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
				
				


                sysmeta = urllib.quote_plus(json.dumps(meta))
                url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s' % (sysaddon, systitle, year, imdb, tvdb, season)

                cm = []				
                try:
                    if season in indicators: 
						cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=6)' % (sysaddon, systitle, imdb, tvdb, season)))
						meta.update({'playcount': 1, 'overlay': 7})
                    else: 
						cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&season=%s&query=7)' % (sysaddon, systitle, imdb, tvdb, season)))
						meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass



                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))

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
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
		
        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
        if "+" in str(myTimeZone): self.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
        else: self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))
		
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.trakt_user = control.setting('trakt.user').strip()
        self.lang = control.apiLanguage()['tvdb']
        self.trakt_sortby = int(control.setting('trakt.sortby'))

        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key.decode('base64'), '%s', '%s')
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'

        self.added_link = 'http://api.tvmaze.com/schedule'
        self.mycalendar_link = 'http://api.trakt.tv/calendars/my/shows/date[29]/60/'
        self.trakthistory_link = 'http://api.trakt.tv/users/me/history/shows?limit=300'
        self.progress_link = 'http://api.trakt.tv/users/me/watched/shows'
        self.hiddenprogress_link = 'http://api.trakt.tv/users/hidden/progress_watched?limit=1000&type=show'
        self.calendar_link = 'http://api.tvmaze.com/schedule?date=%s'

        self.traktlists_link = 'http://api.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api.trakt.tv/users/%s/lists/%s/items'
        self.traktOnDeck_link = 'http://api.trakt.tv/sync/playback/episodes?extended=full&limit=20'
		
    def getLibrary(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, meta=None, idx=True, create_directory=True):
        try:

                self.list = seasons().tvdbLibrary(tvshowtitle, year, imdb, tvdb, 'en', '-1')
                return self.list
        except:
            pass
    def get(self, tvshowtitle, year, imdb, tvdb, season=None, episode=None, meta=None, idx=True, create_directory=True):
        try:
            if idx == True:
                if season == None and episode == None:
                    self.list = cache.get(seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, '-1')
                elif episode == None:
                    self.list = cache.get(seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, season)
                else:
                    self.list = cache.get(seasons().tvdb_list, 1, tvshowtitle, year, imdb, tvdb, self.lang, '-1')
                    num = [x for x,y in enumerate(self.list) if y['season'] == str(season) and  y['episode'] == str(episode)][-1]
                    self.list = [y for x,y in enumerate(self.list) if x >= num]

                if create_directory == True: self.episodeDirectory(self.list)
                return self.list
            else:
                self.list = seasons().tvdb_list(tvshowtitle, year, imdb, tvdb, 'en', '-1')
                return self.list
        except:
            pass


    def calendar(self, url):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            if self.trakt_link in url and url == self.traktOnDeck_link:
                self.blist = cache.get(self.trakt_episodes_list, 720, url, self.trakt_user, self.lang)
                self.list = []
                self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)

            elif self.trakt_link in url and url == self.progress_link:
                self.blist = cache.get(self.trakt_progress_list, 720, url, self.trakt_user, self.lang)
                self.list = []
                self.list = cache.get(self.trakt_progress_list, 0, url, self.trakt_user, self.lang)

            elif self.trakt_link in url and url == self.mycalendar_link:
                self.blist = cache.get(self.trakt_episodes_list, 720, url, self.trakt_user, self.lang)
                self.list = []
                self.list = cache.get(self.trakt_episodes_list, 0, url, self.trakt_user, self.lang)

            elif self.trakt_link in url and '/users/' in url:
                self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)
                self.list = self.list[::-1]

            elif self.trakt_link in url:
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)


            elif self.tvmaze_link in url and url == self.added_link:
                urls = [i['url'] for i in self.calendars(idx=False)][:5]
                self.list = []
                for url in urls:
                    self.list += cache.get(self.tvmaze_list, 720, url, True)

            elif self.tvmaze_link in url:
                self.list = cache.get(self.tvmaze_list, 1, url, False)


            self.episodeDirectory(self.list)
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
        m = control.lang(32060).encode('utf-8').split('|')
        try: months = [(m[0], 'January'), (m[1], 'February'), (m[2], 'March'), (m[3], 'April'), (m[4], 'May'), (m[5], 'June'), (m[6], 'July'), (m[7], 'August'), (m[8], 'September'), (m[9], 'October'), (m[10], 'November'), (m[11], 'December')]
        except: months = []

        d = control.lang(32061).encode('utf-8').split('|')
        try: days = [(d[0], 'Monday'), (d[1], 'Tuesday'), (d[2], 'Wednesday'), (d[3], 'Thursday'), (d[4], 'Friday'), (d[5], 'Saturday'), (d[6], 'Sunday')]
        except: days = []

        for i in range(0, 30):
            try:
                name = (self.datetime - datetime.timedelta(days = i))
                name = (control.lang(32062) % (name.strftime('%A'), name.strftime('%d %B'))).encode('utf-8')
                for m in months: name = name.replace(m[1], m[0])
                for d in days: name = name.replace(d[1], d[0])
                try: name = name.encode('utf-8')
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
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

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
                if tvdb == None or tvdb == '': raise Exception()
                tvdb = re.sub('[^0-9]', '', str(tvdb))

                watched_at = item['last_watched_at']
				
                items.append({'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season, 'enum': episode, 'last_watched_at': watched_at})
            except:
                pass

        try:
            result = trakt.getTraktAsJson(self.hiddenprogress_link)
            result = [str(i['show']['ids']['tvdb']) for i in result]

            items = [i for i in items if not i['tvdb'] in result]
        except:
            pass

        def items_list(i):
            try:
                nextEp = int(i['enum']) + 1
                nextSs = int(i['snum']) + 1
                itemList = []

                try:itemList = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['season'] == i['snum'] and x['episode'] == str(nextEp)][0]
                except:pass
                try: itemList = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['season'] == str(nextSs) and x['episode'] == '1'][0]
                except:pass
                item  = itemList
                if not 'tvshowtitle' in item and len(item) < 1: raise Exception()
                item['action'] = 'episodes'
                item['last_watched_at'] = i['last_watched_at']			
                self.list.append(item)
                return
            except:
                pass
				    
            try:
                tvdbList = cache.get(seasons().tvdb_list, 24, i['tvshowtitle'], i['year'], i['imdb'], i['tvdb'], self.lang, 'nextepisode', i['snum'],  i['enum'])
                item = tvdbList[0]
                item['action'] = 'episodes'
                item['last_watched_at'] = i['last_watched_at']					
                self.list.append(item)
                # print self.list
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


    def trakt_episodes_list(self, url, user, lang):
        items = self.trakt_list(url, user)

        def items_list(i):
            try:
                item = [x for x in self.blist if x['tvdb'] == i['tvdb'] and x['season'] == i['season'] and x['episode'] == i['episode']][0]
                if item['poster'] == '0': raise Exception()
                self.list.append(item)
                return
            except:
                pass

            try:
                url = self.tvdb_info_link % (i['tvdb'], lang)
                data = urllib2.urlopen(url, timeout=10).read()

                zip = zipfile.ZipFile(StringIO.StringIO(data))
                result = zip.read('%s.xml' % lang)
                artwork = zip.read('banners.xml')
                zip.close()

                result = result.split('<Episode>')
                item = [(re.findall('<SeasonNumber>%01d</SeasonNumber>' % int(i['season']), x), re.findall('<EpisodeNumber>%01d</EpisodeNumber>' % int(i['episode']), x), x) for x in result]
                item = [x[2] for x in item if len(x[0]) > 0 and len(x[1]) > 0][0]
                item2 = result[0]

                premiered = client.parseDOM(item, 'FirstAired')[0]
                if premiered == '' or '-00' in premiered: premiered = '0'
                premiered = client.replaceHTMLCodes(premiered)
                premiered = premiered.encode('utf-8')

                try: status = client.parseDOM(item2, 'Status')[0]
                except: status = ''
                if status == '': status = 'Ended'
                status = client.replaceHTMLCodes(status)
                status = status.encode('utf-8')

                title = client.parseDOM(item, 'EpisodeName')[0]
                if title == '': title = '0'
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                season = client.parseDOM(item, 'SeasonNumber')[0]
                season = '%01d' % int(season)
                season = season.encode('utf-8')

                episode = client.parseDOM(item, 'EpisodeNumber')[0]
                episode = re.sub('[^0-9]', '', '%01d' % int(episode))
                episode = episode.encode('utf-8')

                tvshowtitle = i['tvshowtitle']
                imdb, tvdb = i['imdb'], i['tvdb']

                year = i['year']
                try: year = year.encode('utf-8')
                except: pass

                try: poster = client.parseDOM(item2, 'poster')[0]
                except: poster = ''
                if not poster == '': poster = self.tvdb_image + poster
                else: poster = '0'
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: banner = client.parseDOM(item2, 'banner')[0]
                except: banner = ''
                if not banner == '': banner = self.tvdb_image + banner
                else: banner = '0'
                banner = client.replaceHTMLCodes(banner)
                banner = banner.encode('utf-8')

                try: fanart = client.parseDOM(item2, 'fanart')[0]
                except: fanart = ''
                if not fanart == '': fanart = self.tvdb_image + fanart
                else: fanart = '0'
                fanart = client.replaceHTMLCodes(fanart)
                fanart = fanart.encode('utf-8')

                try: thumb = client.parseDOM(item, 'filename')[0]
                except: thumb = ''
                if not thumb == '': thumb = self.tvdb_image + thumb
                else: thumb = '0'
                thumb = client.replaceHTMLCodes(thumb)
                thumb = thumb.encode('utf-8')

                if not poster == '0': pass
                elif not fanart == '0': poster = fanart
                elif not banner == '0': poster = banner

                if not banner == '0': pass
                elif not fanart == '0': banner = fanart
                elif not poster == '0': banner = poster

                if not thumb == '0': pass
                elif not fanart == '0': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
                elif not poster == '0': thumb = poster

                try: studio = client.parseDOM(item2, 'Network')[0]
                except: studio = ''
                if studio == '': studio = '0'
                studio = client.replaceHTMLCodes(studio)
                studio = studio.encode('utf-8')

                try: genre = client.parseDOM(item2, 'Genre')[0]
                except: genre = ''
                genre = [x for x in genre.split('|') if not x == '']
                genre = ' / '.join(genre)
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = client.parseDOM(item2, 'Runtime')[0]
                except: duration = ''
                if duration == '': duration = '0'
                duration = client.replaceHTMLCodes(duration)
                duration = duration.encode('utf-8')

                try: rating = client.parseDOM(item, 'Rating')[0]
                except: rating = ''
                if rating == '': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item2, 'RatingCount')[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item2, 'ContentRating')[0]
                except: mpaa = ''
                if mpaa == '': mpaa = '0'
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                try: director = client.parseDOM(item, 'Director')[0]
                except: director = ''
                director = [x for x in director.split('|') if not x == '']
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                try: writer = client.parseDOM(item, 'Writer')[0]
                except: writer = ''
                writer = [x for x in writer.split('|') if not x == '']
                writer = ' / '.join(writer)
                if writer == '': writer = '0'
                writer = client.replaceHTMLCodes(writer)
                writer = writer.encode('utf-8')

                try: cast = client.parseDOM(item2, 'Actors')[0]
                except: cast = ''
                cast = [x for x in cast.split('|') if not x == '']
                try: cast = [(x.encode('utf-8'), '') for x in cast]
                except: cast = []

                try: plot = client.parseDOM(item, 'Overview')[0]
                except: plot = ''
                if plot == '':
                    try: plot = client.parseDOM(item2, 'Overview')[0]
                    except: plot = ''
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb})
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
                url = url.encode('utf-8')

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
                title = title.encode('utf-8')

                season = item['season']
                season = re.sub('[^0-9]', '', '%01d' % int(season))
                if season == '0': raise Exception()
                season = season.encode('utf-8')

                episode = item['number']
                episode = re.sub('[^0-9]', '', '%01d' % int(episode))
                if episode == '0': raise Exception()
                episode = episode.encode('utf-8')

                tvshowtitle = item['show']['name']
                if tvshowtitle == None or tvshowtitle == '': raise Exception()
                tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
                tvshowtitle = tvshowtitle.encode('utf-8')

                year = item['show']['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year.encode('utf-8')

                imdb = item['show']['externals']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['show']['externals']['thetvdb']
                if tvdb == None or tvdb == '': raise Exception()
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                poster = '0'
                try: poster = item['show']['image']['original']
                except: poster = '0'
                if poster == None or poster == '': poster = '0'
                poster = poster.encode('utf-8')

                try: thumb1 = item['show']['image']['original']
                except: thumb1 = '0'
                try: thumb2 = item['image']['original']
                except: thumb2 = '0'
                if thumb2 == None or thumb2 == '0': thumb = thumb1
                else: thumb = thumb2
                if thumb == None or thumb == '': thumb = '0'
                thumb = thumb.encode('utf-8')

                premiered = item['airdate']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['show']['network']['name']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try: genre = item['show']['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try: duration = item['show']['runtime']
                except: duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration.encode('utf-8')

                try: rating = item['show']['rating']['average']
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating.encode('utf-8')

                try: plot = item['show']['summary']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                itemlist.append({'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': 'Continuing', 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'thumb': thumb})
            except:
                pass

        itemlist = itemlist[::-1]

        return itemlist
		
		
		
    def inProgress(self):
        try:
            from resources.lib.modules import favourites
           
            items = favourites.getProgress('episode')
            self.list = [i[1] for i in items]

            for i in self.list:
                # print "ZEEEEN SELF LIST %s" %i
                if not 'label' in i: i['label'] = '%s (%s)' % (i['title'], i['year'])
                try: i['title'] = i['title'].encode('utf-8')
                except: pass
                try: i['tvshowtitle'] = i['tvshowtitle']
                except: pass

				
                try: i['name'] = i['name'].encode('utf-8')
                except: pass
                if not 'premiered' in i: i['premiered'] = '0'
                if not 'imdb' in i: i['imdb'] = '0'
                if not 'tmdb' in i: i['tmdb'] = '0'
                if not 'tvdb' in i: i['tvdb'] = '0'
                if not 'tvrage' in i: i['tvrage'] = '0'
                if not 'poster' in i: i['poster'] = '0'
                if not 'banner' in i: i['banner'] = '0'
                if not 'fanart' in i: i['fanart'] = '0'
                if not 'season' in i: i['season'] = '0'				
                if not 'episode' in i: i['episode'] = '0'				
                if not 'original_year' in i: i['original_year'] = '0'				

            # self.worker()
            
            self.inProgressDir(self.list)
        except:
            return			
		
		
    def inProgressDir(self, items):
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

        try: multi = [i['tvshowtitle'] for i in items]
        except: multi = []
        multi = len([x for y,x in enumerate(multi) if x not in multi[:y]])
        multi = True if multi > 1 else False

        try: sysaction = items[0]['action']
        except: sysaction = ''

        isFolder = True

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        tvshowBrowserMenu = control.lang(32071).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                if not 'label' in i: i['label'] = i['title']

                if i['label'] == '0':
                    label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                else:
                    label = '%sx%02d . %s' % (i['season'], int(i['episode']), i['label'])
                if multi == True:
                    label = '%s - %s' % (i['tvshowtitle'], label)
					
                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"

                imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                systitle = urllib.quote_plus(i['title'])
                systvshowtitle = urllib.quote_plus(i['tvshowtitle'])
                syspremiered = urllib.quote_plus(i['premiered'])

                bookmarkname = urllib.quote_plus(i['tvshowtitle'].lower())
                bookmarkname = bookmarkname + urllib.quote_plus(' S%02dE%02d' % (int(i['season']), int(i['episode'])))				
                bookmarkname = urllib.unquote_plus(self.bookmarkname)
				
                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
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

                sysmeta = urllib.quote_plus(json.dumps(meta))


                url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season)
                sysurl = urllib.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered)

                if isFolder == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season, episode)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                if multi == True:
                    cm.append((tvshowBrowserMenu, 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))

                try:
                    overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tvdb, season, episode))

                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, systvshowtitle, tvdb)))


                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))


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

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
				
                played = bookmarks.bookmarks().get(bookmarkname.lower())
                item.setProperty('resumetime', played)

                item.setInfo(type='Video', infoLabels = meta)

                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except:
                pass

        control.content(syshandle, 'episodes')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('episodes', {'skin.estuary': 55, 'skin.confluence': 504})

		
		


    def episodeDirectory(self, items):
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

        try: multi = [i['tvshowtitle'] for i in items]
        except: multi = []
        multi = len([x for y,x in enumerate(multi) if x not in multi[:y]])
        multi = True if multi > 1 else False

        try: sysaction = items[0]['action']
        except: sysaction = ''

        isFolder = False

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        tvshowBrowserMenu = control.lang(32071).encode('utf-8')

        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                if not 'label' in i: i['label'] = i['title']

                if i['label'] == '0':
                    label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                else:
                    label = '%sx%02d . %s' % (i['season'], int(i['episode']), i['label'])
                if multi == True:
                    label = '%s - %s' % (i['tvshowtitle'], label)
					
                season_check = i['premiered']
                if int(re.sub('[^0-9]', '', str(season_check))) > int(re.sub('[^0-9]', '', str(self.today_date))): label = "[I][COLOR yellow]" + label + "[/COLOR][/I]"

                imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                systitle = urllib.quote_plus(i['title'])
                systvshowtitle = urllib.quote_plus(i['tvshowtitle'])
                syspremiered = urllib.quote_plus(i['premiered'])

                bookmarkname = urllib.quote_plus(i['tvshowtitle'].lower())
                bookmarkname = bookmarkname + urllib.quote_plus(' S%02dE%02d' % (int(i['season']), int(i['episode'])))				
                bookmarkname = urllib.unquote_plus(bookmarkname)

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
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

                sysmeta = urllib.quote_plus(json.dumps(meta))


                url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)
                sysurl = urllib.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered)

                if isFolder == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tvdb, season, episode)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                if multi == True:
                    cm.append((tvshowBrowserMenu, 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tvdb)))

                try:
                    overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tvdb, season, episode))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=6)' % (sysaddon, imdb, tvdb, season, episode)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=episodePlaycount&imdb=%s&tvdb=%s&season=%s&episode=%s&query=7)' % (sysaddon, imdb, tvdb, season, episode)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, systvshowtitle, tvdb)))


                if isOld == True:
				
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))
					
					
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

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
                played = bookmarks.bookmarks().get(bookmarkname)
                item.setProperty('resumetime', played)
                item.setInfo(type='Video', infoLabels = meta)

                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)

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

        queueMenu = control.lang(32065).encode('utf-8')

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


