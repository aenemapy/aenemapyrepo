
from resources.lib.modules import control
from resources.lib.modules import client
import requests
import os,sys,re,json,urllib,urlparse,base64,datetime,time,json
params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
tmdbApi = control.setting('tmdb.api')
tmdb_image = 'https://image.tmdb.org/t/p/original'
tmdb_poster = 'https://image.tmdb.org/t/p/w500'
tmdb_by_query_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id&append_to_response=external_ids' % ("%s", tmdbApi)	
# TMDB MOVIE/TV DETAILS'#######################
tmdb_movie_page = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US&append_to_response=external_ids,credits' % ("%s", tmdbApi)
tmdb_tv_page = 'https://api.themoviedb.org/3/tv/%s?api_key=%s&language=en-US&append_to_response=external_ids' % ("%s", tmdbApi)
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
			
            # print ("TMDB API MOVIES", item)
            title = item['title']
            if title == '' or title == None: title = '0'
            title = title.encode('utf-8')	

            tmdb = item['id']
            if tmdb == '' or tmdb == None: tmdb = '0'
            tmdb = re.sub('[^0-9]', '', str(tmdb))
            tmdb = tmdb.encode('utf-8')
            # print ("TMDB API tmdb", tmdb)			
            poster = item['poster_path']
            if poster == '' or poster == None: poster = '0'
            if not poster == '0': poster = '%s%s' % (tmdb_poster, poster)
            poster = poster.encode('utf-8')
            # print ("TMDB API poster", poster)		
            fanart = item['backdrop_path']
            if fanart == '' or fanart == None: fanart = '0'
            if not fanart == '0': fanart = '%s%s' % (tmdb_image, fanart)
            fanart = fanart.encode('utf-8')
            # print ("TMDB API fanart", fanart)	

            meta = {'tmdb': tmdb, 'title': title, 'poster': poster, 'fanart': fanart}

            return meta

        except:
            meta = '0'
	
            
            return meta

	
def getDetails(id):
    id = id
    url = tmdb_movie_page % id
    try:
		result = requests.get(url)
		response = result.status_code
		if str(response) == '429':
			print ("------ WAITING FOR TMDB TO REFRESH RATE LIMIT -------------")
			time.sleep(10)
			result = requests.get(url)
		result = json.loads(result.content)

		return result

    except: return '0'
	
def request(url):
    try:
		url = url % tmdbApi
		print "[TMDB REQUEST] >>> %s " % url
		result = requests.get(url)
		response = result.status_code
		if str(response) == '429':
			print ("------ WAITING FOR TMDB TO REFRESH RATE LIMIT -------------")
			time.sleep(10)
			result = requests.get(url)
		return result.content
    except: return '0'