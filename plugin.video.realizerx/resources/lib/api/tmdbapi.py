
from resources.lib.modules import control
from resources.lib.modules import client
import requests
import urllib.parse as urlparse
import os,sys,re,json,urllib.request,urllib.parse,urllib.error,base64,datetime,time,json
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
API_KEY = control.setting('tmdb.api')
if API_KEY == '' or API_KEY == None: API_KEY = 'e899af1690e0b4590783a9374869b4d5'
tmdb_image = 'https://image.tmdb.org/t/p/original'
tmdb_poster = 'https://image.tmdb.org/t/p/w500'
tmdb_by_query_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id&append_to_response=external_ids' % ("%s", API_KEY)    
# TMDB MOVIE/TV DETAILS'#######################
api_list    = ['e899af1690e0b4590783a9374869b4d5', '4a8bcd0ac34204444664efd97fff827c', '3b369c64331e23eb91005d6373e1f9f5', '81b40753b50ef92a9ce1c49973095a70']

TMDB_VERSION = 'https://api.themoviedb.org/3/'
tmdb_image = 'https://image.tmdb.org/t/p/original'
tmdb_poster = 'https://image.tmdb.org/t/p/w500'


# TMDB MOVIE/TV DETAILS'#######################
tmdb_movie_page      = TMDB_VERSION + 'movie/%s?api_key=%s&language=en-US&append_to_response=external_ids,credits,release_dates' 
tmdb_tv_page         = TMDB_VERSION + 'tv/%s?api_key=%s&language=en-US&append_to_response=external_ids,credits' 
tmdb_episode_page    = TMDB_VERSION + 'tv/%s/season/%s?api_key=%s&language=en-US'

tmdb_by_query_tvdb   = TMDB_VERSION + 'find/%s?api_key=%s&external_source=tvdb_id&language=en-US&append_to_response=external_ids'
tmdb_by_query_imdb   = TMDB_VERSION + 'find/%s?api_key=%s&external_source=imdb_id&language=en-US&append_to_response=external_ids'
tmdb_videos          = TMDB_VERSION + '%s/%s/videos?api_key=%s'
next_airing_episode  = TMDB_VERSION + 'tv/%s?api_key=%s&language=en-US' 
movie_genres         = TMDB_VERSION + 'genre/movie/list?api_key=%s&language=en-US'
tv_genres            = TMDB_VERSION + 'genre/tv/list?api_key=%s&language=en-US'
popular_persons      = TMDB_VERSION + 'person/popular?api_key=%s&language=en-US&page=1'
tmdb_single_episode  = TMDB_VERSION + 'tv/%s/season/%s/episode/%s?api_key=%s&language=en-US'

def getImdb(imdb):
    url = tmdb_by_query_imdb % imdb
    try: result = requests.get(url, timeout=5).content
    except requests.Timeout as err: control.infoDialog('TMDB API is Slow, Please Try Later...', time=1)
    return result

    

def getMoviesbyImdb(imdb):
        try:
            url = tmdb_by_query_imdb % imdb
            result = requests.get(url).json()

            item = result['movie_results'][0]
            
            # #print ("TMDB API MOVIES", item)
            title = item['title']
            if title == '' or title == None: title = '0'
            title = title   

            tmdb = item['id']
            if tmdb == '' or tmdb == None: tmdb = '0'
            tmdb = re.sub('[^0-9]', '', str(tmdb))
            tmdb = tmdb
            # #print ("TMDB API tmdb", tmdb)         
            poster = item['poster_path']
            if poster == '' or poster == None: poster = '0'
            if not poster == '0': poster = '%s%s' % (tmdb_poster, poster)
            poster = poster
            # #print ("TMDB API poster", poster)     
            fanart = item['backdrop_path']
            if fanart == '' or fanart == None: fanart = '0'
            if not fanart == '0': fanart = '%s%s' % (tmdb_image, fanart)
            fanart = fanart
            # #print ("TMDB API fanart", fanart) 

            meta = {'tmdb': tmdb, 'title': title, 'poster': poster, 'fanart': fanart}

            return meta

        except:
            meta = '0'
    
            
            return meta

    
   
def request(url):
    try:
        url = url % API_KEY
        #print("[TMDB REQUEST] >>> %s " % url)
        result = requests.get(url)
        response = result.status_code
        if str(response) == '429':
            #print ("------ WAITING FOR TMDB TO REFRESH RATE LIMIT -------------")
            time.sleep(10)
            result = requests.get(url)
        return result.content
    except: return '0'

def getSingleEp(id, season, episode):
    url = tmdb_single_episode % (id, season, episode, "%s")
    try:
        result = tmdbRequest(url)
        result = json.loads(result)
        return result

    except: return '0'
  
def getNextAiring(tmdb):
    myTimeDelta = 0
    myTimeZone = control.setting('setting.timezone')
    myTimeDelta = int(re.sub('[^0-9]', '', str(myTimeZone)))
    if "+" in str(myTimeZone): datetimeUTC = datetime.datetime.utcnow() + datetime.timedelta(hours = int(myTimeDelta))
    else: datetimeUTC = datetime.datetime.utcnow() - datetime.timedelta(hours = int(myTimeDelta))
        
    Today = (datetimeUTC).strftime('%Y-%m-%d')
    
    url = next_airing_episode % (tmdb, "%s")
    result = json.loads(tmdbRequest(url))
    
    #Today = '2020-01-14'
    try:
        lastAirDate = result['last_episode_to_air']['air_date']

        if str(lastAirDate) == str(Today):

            season = result['last_episode_to_air']['season_number']
            episode = result['last_episode_to_air']['episode_number']
            return str(season), str(episode)
    except:pass
    
    try:
        nextAirDate = result['next_episode_to_air']['air_date']
        if str(nextAirDate) == str(Today):
            season = result['next_episode_to_air']['season_number']
            episode = result['next_episode_to_air']['episode_number']
            return str(season), str(episode)
    except:pass
    
    return None, None
            
def getOriginaltitle(imdb):
    langs = ['en', 'en-us']
    url = tmdb_by_query_imdb % (imdb, "%s")
    result = json.loads(tmdbRequest(url))
    item = result['movie_results'][0]
    original_title = item['original_title']
    original_lang = item['original_language']
    if original_lang.lower() in langs: title = original_title
    else: title = item['title']
    return title

def movieGenres():
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = movie_genres
    result = cache.get(tmdbRequest, 720, url)
    result = json.loads(result)
    genres = result['genres']
    return genres
    
def tvGenres():
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = tv_genres
    result = cache.get(tmdbRequest, 720, url)
    result = json.loads(result)
    genres = result['genres']
    return genres
    
def moviePerson(id):
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = popular_persons
    result = cache.get(tmdbRequest, 720, url)
    result = json.loads(result)
    return genres
    
def popularPersons():
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = popular_persons
    result = cache.get(tmdbRequest, 24, url)
    result = json.loads(result)
    #print ("TMDB POPULAR PERSONS", result)
    return result
    
def getImdb(imdb):
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = tmdb_by_query_imdb % (imdb, "%s")
    result = cache.get(tmdbRequest, 720, url)
    return result
    
def getTvdb(tvdb):
    # NOT CONVERT TO JSON AS IT WILL BE CONVERTED LATER
    url = tmdb_by_query_tvdb % (tvdb, "%s")
    result = cache.get(tmdbRequest, 720, url)
    return result

def getMoviesbyImdb(imdb):
        try:
            url = tmdb_by_query_imdb % (imdb, "%s")
            result = cache.get(tmdbRequest, 720, url)
            result = json.loads(result)

            item = result['movie_results'][0]
            
            # #print ("TMDB API MOVIES", item)
            title = item['title']
            if title == '' or title == None: title = '0'
            title = title.encode('utf-8')   

            tmdb = item['id']
            if tmdb == '' or tmdb == None: tmdb = '0'
            tmdb = re.sub('[^0-9]', '', str(tmdb))
            tmdb = tmdb.encode('utf-8')
            # #print ("TMDB API tmdb", tmdb)         
            poster = item['poster_path']
            if poster == '' or poster == None: poster = '0'
            if not poster == '0': poster = '%s%s' % (tmdb_poster, poster)
            poster = poster.encode('utf-8')
            # #print ("TMDB API poster", poster)     
            fanart = item['backdrop_path']
            if fanart == '' or fanart == None: fanart = '0'
            if not fanart == '0': fanart = '%s%s' % (tmdb_image, fanart)
            fanart = fanart.encode('utf-8')
            # #print ("TMDB API fanart", fanart) 

            meta = {'tmdb': tmdb, 'title': title, 'poster': poster, 'fanart': fanart}

            return meta

        except:
            meta = '0'
    
            
            return meta

def getTrailers(imdb, query):
        sources = []
        try:
            if query=='movie': 
                url = tmdb_by_query_imdb % (imdb, "%s")
                result = json.loads(tmdbRequest(url))
                item = result['movie_results'][0]

            elif query=='tv': 
                url = tmdb_by_query_imdb % (imdb, "%s")
                result = json.loads(tmdbRequest(url))
                item = result['tv_results'][0]
                        
            #print ("TMDB API TRAILERS", item)

            tmdb = item['id']
            if tmdb == '' or tmdb == None: tmdb = '0'
            tmdb = re.sub('[^0-9]', '', str(tmdb))
            tmdb = tmdb.encode('utf-8')
            
            videos = tmdb_videos % (query, tmdb, "%s")
            r = json.loads(tmdbRequest(videos))
            r = r['results']
            
            videosources = [i for i in r if i['site'].lower() == 'youtube']
        
            for v in videosources:
                title = v['name']
                trailer = v['key']

                meta = {'trailer': trailer, 'title': title}
                sources.append(meta)

            return sources

        except:
            return sources
            
def getEpisodes(id, season=''):
    url = tmdb_episode_page % (id, season, "%s")
    try:
        result = tmdbRequest(url)
        result = json.loads(result)
        return result

    except: return '0'
    
def getDetails(id, tv=False):
    id = id
    if tv == True: url = tmdb_tv_page % (id, "%s")
    else: url = tmdb_movie_page % (id, "%s")
    try:
        result = tmdbRequest(url)
        result = json.loads(result)
        return result
    except: return '0'
    
def tmdbRequest(url):
    try:
        url = url % API_KEY
        print ("[TMDB REQUEST] >>> %s " % url)
        try: result = requests.get(url, timeout=10)
        except requests.Timeout as err: control.infoDialog('TMDB API is Slow, Please Try Later...', time=1)
        
        response = result.status_code
        if response == 429:
            timetowait = int(result.headers['Retry-After']) + 1
            waitLabel = "------ WAITING FOR TMDB TO REFRESH RATE LIMIT : %s SEC LEFT -------------" % str(timetowait)
            #print (waitLabel)
            time.sleep(timetowait)
            try:
                result = requests.get(url, timeout=10)
            except requests.Timeout as err:
                control.infoDialog('TMDB API is Slow, Please Try Later...', time=1)
                
        return result.content
    except: return '0'
