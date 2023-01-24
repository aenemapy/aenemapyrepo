
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import workers
from datetime import datetime, date, timedelta
import requests
import os,sys,re,json,urllib.request,urllib.parse,urllib.error,base64,time,json
import urllib.parse as urlparse
import xbmc, xbmcaddon, xbmcvfs
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
tvdbApi = control.setting('tvdb.api')
# tvdbUsername = control.setting('tvdb.username')
# tvdbUserKey = control.setting('tvdb.userkey')

addonInfo = xbmcaddon.Addon().getAddonInfo
profilePath = xbmcvfs.translatePath(addonInfo('profile'))
tvdbSettings = os.path.join(profilePath, 'tvdb.json')

tvdb2_api = 'https://api.thetvdb.com'
tvdb2_info_series = 'https://api.thetvdb.com/series/%s'
tvdb2_series_poster = 'https://api.thetvdb.com/series/%s/images/query?keyType=poster'
tvdb2_series_fanart = 'https://api.thetvdb.com/series/%s/images/query?keyType=fanart'
tvdb2_series_banner = 'https://api.thetvdb.com/series/%s/images/query?keyType=series'
tvdb2_series_season = 'https://api.thetvdb.com/series/%s/images/query?keyType=season'
tvdb2_series_bannerseason = 'https://api.thetvdb.com/series/%s/images/query?keyType=seasonwide'
tvdb2_by_imdb = 'https://api.thetvdb.com/search/series?imdbId=%s'
tvdb2_by_query = 'https://api.thetvdb.com/search/series?name=%s'
tvdb2_series_actors = 'https://api.thetvdb.com/series/%s/actors'
tvdb_image = 'http://thetvdb.com/banners/'
tvdb_favourites = 'https://api.thetvdb.com/user/favorites'

tvdbLang = control.apiLanguage()['tvdb']


def checkTVDB(url, headers):
    refresh = datetime.now().strftime('%Y%m%d%H%M')
    refresh = re.sub('[^0-9]', '', str(refresh))
    data = {}
    with open(tvdbSettings) as json_file:
        try:
            data = json.load(json_file)
            refreshTime = data['check']
        except:
            refreshTime = None
    if refreshTime == None or refreshTime == '' or refreshTime == '0':
        data['check'] = refresh
        with open(tvdbSettings, 'w') as outfile: json.dump(data, outfile, indent=2)
        try: result = requests.get(url, headers=headers, timeout=5)
        except requests.Timeout as err: control.infoDialog('TVDB API is Slow, Please Try Later...', time=1)
    else:
        update = int(refresh) - int(refreshTime)
        if update > 5:
            data['check'] = refresh
            with open(tvdbSettings, 'w') as outfile: json.dump(data, outfile)
            try: result = requests.get(url, headers=headers, timeout=5)
            except requests.Timeout as err: control.infoDialog('TVDB API is Slow, Please Try Later...', time=1)

def createJson():
    data = {'added':'0', 'token':'0','check':'0'}
    with open(tvdbSettings, 'w') as outfile: json.dump(data, outfile, indent=2)

def authTvdb():
    oauth = "https://api.thetvdb.com/login"
    headers = {'accept-encoding': 'gzip', 'accept-language': 'en', 'Content-Type': 'application/json', 'apikey': tvdbApi}
    auth_post = {'apikey': tvdbApi}
    result = requests.post(oauth, data=json.dumps(auth_post), headers=headers).json()
    token = result['token']
    timeNow = datetime.now().strftime('%Y%m%d%H%M')
    timeNow = re.sub('[^0-9]', '', str(timeNow))
    data = {'added':str(timeNow), 'token':token}
    with open(tvdbSettings, 'w') as outfile: json.dump(data, outfile, indent=2)
    #print(("AUTH TOKEN RESET", token))
    return token

def getToken():
    if not os.path.exists(tvdbSettings): createJson()
    timeAdded = 0
    try:
        with open(tvdbSettings) as json_file:
            try:
                data = json.load(json_file)
                token = data['token']
                timeAdded = data['added']
            except:
                token = None
        if token == '' or token == None or token =='0':
            #print ("TOKEN IS NONE")
            token = authTvdb()
            return token
        refresh = datetime.now().strftime('%Y%m%d%H%M')
        refresh = re.sub('[^0-9]', '', str(refresh))
        update = int(refresh) - int(timeAdded)
        if update > 1000: token = authTvdb()
        return token
    except: return

def getTvdb(url, timeout=30):
    token = getToken()
    headers = {'Accept-Language': 'en', 'Content-Type': 'application/json'}
    headers['Authorization'] = 'Bearer %s' % token
    checkTVDB(url, headers)
    try: result = requests.get(url, headers=headers, timeout=timeout).content
    except requests.Timeout as err: control.infoDialog('TVDB API is Down...', time=1)
    return result

def getTvdbTranslation(tvdb, timeout=30):
    url = tvdb2_info_series % tvdb
    token = getToken()
    headers = {'accept-encoding': 'gzip', 'accept-language': tvdbLang, 'Content-Type': 'application/json',  'apikey': tvdbApi}
    headers['Authorization'] = 'Bearer %s' % token
    checkTVDB(url, headers)
    try: result = requests.get(url, headers=headers, timeout=timeout).content
    except requests.Timeout as err: control.infoDialog('TVDB API is Down...', time=1)
    return result

def forceToken():

        token = authTvdb()
        refresh =  datetime.now().strftime('%Y%m%d%H%M')
        refresh =  re.sub('[^0-9]', '', str(refresh))
        control.setSetting(id='tvdb.refresh', value=refresh)
        control.infoDialog('TVDB TOKEN UPDATED', sound=True, icon='INFO')

def addTvShow(title, tvdb):
    token = getToken()
    url = '/%s' % tvdb
    url = tvdb_favourites + url

    headers = {'accept-encoding': 'gzip', 'accept-language': 'en', 'Content-Type': 'application/json', 'apikey': tvdbApi}
    headers['Authorization'] = 'Bearer %s' % token
    auth_post = {'apikey': tvdbApi}
    result = requests.put(url, data=json.dumps(auth_post), headers=headers)
    control.infoDialog('Added to Tvdb', heading=title)

def removeTvShow(tvdb):
    token = getToken()
    url = '/%s' % tvdb
    url = tvdb_favourites + url

    headers = {'accept-encoding': 'gzip', 'accept-language': 'en-US', 'Content-Type': 'application/json', 'apikey': tvdbApi}
    headers['Authorization'] = 'Bearer %s' % token
    auth_post = {'apikey': tvdbApi }
    result = requests.delete(url, data=json.dumps(auth_post), headers=headers)
    control.refresh()

def getFav():
    token = getToken()
    url = tvdb_favourites
    headers = {'accept-encoding': 'gzip', 'accept-language': 'en-US', 'Content-Type': 'application/json', 'apikey': tvdbApi}
    headers['Authorization'] = 'Bearer %s' % token
    auth_post = {'apikey': tvdbApi }
    result = requests.get(url, params=json.dumps(auth_post), headers=headers)


    return result.content

def getPoster(tvdb):
    try:

        art = tvdb2_series_poster % tvdb

        art = getTvdb(art)
        art = json.loads(art)
        art = art['data']
        try:
            poster = [(x['fileName'],x['ratingsInfo']['count']) for x in art if not x['ratingsInfo']['count'] == '']
            poster = [(x[0],x[1]) for x in poster]
            poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)
            poster = [(x[0]) for x in poster][0]
            poster = poster

        except: poster = ''
        if not poster == '': poster = tvdb_image + poster
        else: poster = '0'
        return poster

    except:
        poster = '0'
        return poster

def getFanart(tvdb):
    try:

        art = tvdb2_series_fanart % tvdb
        art = getTvdb(art)
        art = json.loads(art)
        art = art['data']
        try:
            fanart = [(x['fileName'],x['ratingsInfo']['count']) for x in art if not x['ratingsInfo']['count'] == '']
            fanart = [(x[0],x[1]) for x in fanart]
            fanart = sorted(fanart, key = lambda x : int(x[1]), reverse= True)
            fanart = [(x[0]) for x in fanart][0]
            fanart = fanart

        except: fanart = ''
        if not fanart == '': fanart = tvdb_image + fanart
        else: fanart = '0'
        return fanart

    except:
        fanart = '0'
        return fanart

def getBanner(tvdb):
    try:

        art = tvdb2_series_banner % tvdb
        art = getTvdb(art)
        art = json.loads(art)
        art = art['data']
        try:
            banner = [(x['fileName'],x['ratingsInfo']['count']) for x in art if not x['ratingsInfo']['count'] == '']
            banner = [(x[0],x[1]) for x in banner]
            banner = sorted(banner, key = lambda x : int(x[1]), reverse= True)
            banner = [(x[0]) for x in banner][0]
            banner = banner

        except: banner = ''
        if not banner == '': banner = tvdb_image + banner
        else: banner = '0'
        return banner

    except:
        banner = '0'
        return banner

def getSeasonPoster(tvdb,season):
    try:
        art = "https://api.thetvdb.com/series/%s/images/query?keyType=season&subKey=%s" % (tvdb, season)
        art = getTvdb(art)
        art = json.loads(art)
        art = art['data']


        try:
            poster = [(x['fileName'],x['ratingsInfo']['count']) for x in art if not x['ratingsInfo']['count'] == '']
            poster = [(x[0],x[1]) for x in poster]
            poster = sorted(poster, key = lambda x : int(x[1]), reverse= True)
            poster = [(x[0]) for x in poster][0]
            poster = poster

        except: poster = ''
        if not poster == '': poster = tvdb_image + poster
        else: poster = '0'
        return poster

    except:
        poster = '0'
        return poster

def getSeasonsFull(tvdb):
    try:
        art = "https://api.thetvdb.com/series/%s/images/query?keyType=season" % (tvdb)


        art = getTvdb(art)

        art = json.loads(art)
        art = art['data']
        season_art = []

        try:
            poster = [(x['fileName'],x['subKey'],x['ratingsInfo']['count']) for x in art]
            poster = [(x[0],x[1],x[2]) for x in poster]
            posterid = [x[2] for x in poster]
            poster = sorted(poster, key = lambda x : int(x[2]), reverse= True)
            poster = [(x[0],x[1]) for x in poster]

            for file,season in poster:
                # #print ("TVDB API POSTER 3", season, rating)
                if not season in season_art: season_art.append([file,season])

        except:
            season_art = '0'

        return season_art

    except:

        return '0'


class airingtoday:
    def __init__(self):
        self.priority = 0


        self.date = date.today()
        self.today = datetime.now().strftime('%Y%m%d')
        self.today = re.sub('[^0-9]', '', str(self.today))

        yesterday = date.today() - timedelta(1)
        self.yesterday = yesterday.strftime('%Y%m%d')
        self.yesterday = re.sub('[^0-9]', '', str(self.yesterday))
        self.items = []

    def get(self):
        self.items = []
        threads = []

        try:
            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties" : ["thumbnail", "imdbnumber", "title", "year"]}, "id": 1}')
            lib = str(lib, 'utf-8', errors='ignore')
            lib = json.loads(lib)['result']['tvshows']

            for item in lib:
                poster = item['thumbnail']
                title = item['title']
                imdb = item['imdbnumber']

                w = workers.Thread(self.getTvdbAiring, imdb, title, poster)
                threads.append(w)

            [i.start() for i in threads]

            for i in range(0, 60):
                is_alive = [x for x in threads if x.is_alive() == True]
                if not is_alive: break
                time.sleep(1)
        except:pass
        for title, poster, label in self.items:
            control.infoDialog(label, heading=title.upper(), icon=poster)
            time.sleep(3)


    def getTvdbAiring(self, ids, title, poster):
        from datetime import date, datetime, time, timedelta
        myTimeDelta = 0
        myTimeZone = control.setting('setting.timezone')
        myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))

        #print(("TIMEZONE", myTimeZone, myTimeDelta))
        try:

            try:
                s = tvdb2_api + "/series/%s" % str(ids)
                s = getTvdb(s)
                api = json.loads(s)
                airTime = api['data']['airsTime']
                try: network = api['data']['network']
                except: network = ''
                try:
                    at = convert_time_list(airTime)
                except: at = None
            except: at = None

            if at == None: epTimeLabel = 'ND'
            else:
                try:
                    atHour = int(at['hour'])
                    atMin = int(at['min'])

                    if "+" in str(myTimeZone): dt = datetime.combine(date.today(), time(atHour, atMin)) + timedelta(hours=myTimeDelta)
                    else: dt = datetime.combine(date.today(), time(atHour, atMin)) - timedelta(hours=myTimeDelta)

                    epTime = dt.strftime("%H:%M")
                    epTimeLabel = str(epTime) + " (" + str(myTimeZone) + ")"

                    # timeUTC = datetime.now()
                    # timeUTCY = datetime.now() - timedelta(1)
                    # # ### TODAY   #####
                    # timeUTC = timeUTC + timedelta(hours=5)
                    # timeUTC = timeUTC.strftime("%Y%m%d")
                    # timeUTC = re.sub('[^0-9]', '', str(timeUTC))
                    # if str(timeUTC) == str(self.today):   checkDate = self.today




                    # else:
                        # # ### YESTERDAY #####
                        # timeUTCY = timeUTCY.replace(hour=atHour)
                        # timeUTCY = timeUTCY + timedelta(hours=5)
                        # timeUTCY = timeUTCY.strftime("%Y%m%d")
                        # timeUTCY = re.sub('[^0-9]', '', str(timeUTCY))
                        # if str(timeUTCY) == str(self.today): checkDate = self.yesterday

                except: epTimeLabel = 'ND'
            checkDate = self.today
            if checkDate == '0' or checkDate == '' or checkDate == None: raise Exception()
            # #print ("DATE TO CHECK", checkDate)
            r = tvdb2_api + "/series/%s/episodes" % str(ids)
            r = getTvdb(r)
            api = json.loads(r)
            api = api['data']
            totalEpisodes = [(i['airedSeason'],i['airedEpisodeNumber']) for i in api if str(re.sub('[^0-9]', '', str(i['firstAired']))) == str(checkDate)]
            for season, episode in totalEpisodes:
                labelHead = title + " - " + str(season) + "x" + str(episode)
                label = "Airing Today: " + epTimeLabel
                if network != '' and network != None:
                    label = label + " on " + str(network)
                self.items.append([labelHead,poster,label])

            return self.items
        except:pass


def convert_date(date_string):
        """Convert a thetvdb date string into a datetime.date object."""
        first_aired = None
        try:
            first_aired = date(*list(map(int, date_string.split("-"))))
        except ValueError:
            pass

        return first_aired

def convert_time(time_string):
        import datetime
        """Convert a thetvdb time string into a datetime.time object."""
        time_res = [re.compile(r"\D*(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?.*(?P<ampm>a|p)m.*", re.IGNORECASE), # 12 hour
                    re.compile(r"\D*(?P<hour>\d{1,2}):?(?P<minute>\d{2}).*")]                                     # 24 hour

        for r in time_res:
            m = r.match(time_string)
            if m:
                gd = m.groupdict()

                if "hour" in gd and "minute" in gd and gd["minute"] and "ampm" in gd:
                    hour = int(gd["hour"])
                    if hour == 12:
                        hour = 0
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    return datetime.time(hour, int(gd["minute"]))
                elif "hour" in gd and "ampm" in gd:
                    hour = int(gd["hour"])
                    if hour == 12:
                        hour = 0
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    return datetime.time(hour, 0)
                elif "hour" in gd and "minute" in gd:
                    return datetime.time(int(gd["hour"]), int(gd["minute"]))

        return None


def convert_time_list(time_string):
        """Convert a thetvdb time string into a datetime.time object."""
        time_res = [re.compile(r"\D*(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?.*(?P<ampm>a|p)m.*", re.IGNORECASE), # 12 hour
                    re.compile(r"\D*(?P<hour>\d{1,2}):?(?P<minute>\d{2}).*")]                                     # 24 hour

        for r in time_res:
            m = r.match(time_string)
            if m:
                gd = m.groupdict()

                if "hour" in gd and "minute" in gd and gd["minute"] and "ampm" in gd:
                    hour = int(gd["hour"])
                    if hour == 12:
                        hour = 0
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    converted = {'hour':hour, 'min':int(gd["minute"])}
                    return converted

                elif "hour" in gd and "ampm" in gd:
                    hour = int(gd["hour"])
                    if hour == 12:
                        hour = 0
                    if gd["ampm"].lower() == "p":
                        hour += 12

                    converted = {'hour':hour, 'min':0}
                    return converted

                elif "hour" in gd and "minute" in gd:

                    converted = {'hour':int(gd["hour"]), 'min':int(gd["minute"])}
                    return converted


        return None



