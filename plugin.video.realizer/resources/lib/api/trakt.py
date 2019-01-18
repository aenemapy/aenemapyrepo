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


import re,json,urlparse,time

from resources.lib.modules import cache
from resources.lib.modules import control
from resources.lib.modules import cleandate
from resources.lib.modules import client
from resources.lib.modules import utils
from resources.lib.modules import log_utils
import requests


BASE_URL = 'https://api.trakt.tv'
CLIENT_ID = '4cd75230b8878f917d2000e3f3a2f650e742e5789ad981ea1096372ad57285d5'  # CLIENT ID
CLIENT_SECRET = 'e0278e4fe47c9cdba9cf22d4fca1b36040ea354df95839d06bb12cd321dac57a'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

sync_history = ['https://api.trakt.tv/sync/history']

post_links = ['/sync/history', '/oauth/' , '/scrobble/', '/sync/collection', '/sync/collection/remove', '/sync/watchlist', '/sync/watchlist/remove' ] 
def __getTrakt(url, post=None):
    try:
        url = urlparse.urljoin(BASE_URL, url)
        post = json.dumps(post) if post else None
		
        if post == None: post == ''
        headers = {'Content-Type': 'application/json', 'trakt-api-key': CLIENT_ID, 'trakt-api-version': '2'}
		

        if getTraktCredentialsInfo():
            headers.update({'Authorization': 'Bearer %s' % control.setting('trakt.token')})
			
        if any(value in url for value in post_links): result = requests.post(url, data=post, headers=headers) 
        		
        else: result = requests.get(url, params=post, headers=headers)
		
        resp_code = str(result.status_code)
        resp_header = result.headers
        result = result.content		
		
        # print ("TRAKT url", url)		
        # print ("TRAKT RESULT", result)		
		
			

        if resp_code in ['500', '502', '503', '504', '520', '521', '522', '524']:
            log_utils.log('Temporary Trakt Error: %s' % resp_code, log_utils.LOGWARNING)
            
            return
        elif resp_code in ['404']:
            log_utils.log('Object Not Found : %s' % resp_code, log_utils.LOGWARNING)
            return

        if resp_code not in ['401', '405']:
            return result, resp_header

        oauth = urlparse.urljoin(BASE_URL, '/oauth/token')
        opost = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'redirect_uri': REDIRECT_URI, 'grant_type': 'refresh_token', 'refresh_token': control.setting('trakt.refresh')}

        result = requests.post(oauth, data=json.dumps(opost), headers=headers).content
        result = utils.json_loads_as_str(result)
        # print ("TRAKT RESULT2", result)		
		

        token, refresh = result['access_token'], result['refresh_token']

        control.setSetting(id='trakt.token', value=token)
        control.setSetting(id='trakt.refresh', value=refresh)

        headers['Authorization'] = 'Bearer %s' % token

        if any(value in url for value in post_links): result = requests.post(url, data=post, headers=headers) 
        elif url in sync_history: result = requests.post(url, data=post, headers=headers) 		
        else: result = requests.get(url, params=post, headers=headers)	
		
        resp_header2 = result.headers
        result2 = result.content	
        return result2, resp_header2
	
		
				
		
		
    except Exception as e:
        log_utils.log('Unknown Trakt Error: %s' % e, log_utils.LOGWARNING)
        pass

def getTraktAsJson(url, post=None):
    try:
        r, res_headers = __getTrakt(url, post)
        r = utils.json_loads_as_str(r)
        if 'X-Sort-By' in res_headers and 'X-Sort-How' in res_headers:
            r = sort_list(res_headers['X-Sort-By'], res_headers['X-Sort-How'], r)
        return r
    except:
        pass
		
def checkCredentials():
    user = control.setting('trakt.user')
    token = control.setting('trakt.token') 
    if user == '' or user == None: check = 'false'
    elif token == '' or token == None: check = 'false'
    else: check = 'true'
    return check
	

def authTrakt():
    try:

        check = checkCredentials()
        if check == 'true':
			yes = control.yesnoDialog(control.lang(32511).encode('utf-8'), control.lang(32512).encode('utf-8'), '', 'Trakt')
			if yes:
				control.setSetting(id='trakt.user', value='')
				control.setSetting(id='trakt.token', value='')
				control.setSetting(id='trakt.refresh', value='')
				control.infoDialog('Trakt Account Reset: DONE', sound=True, icon='INFO')
			raise Exception()

        result = getTraktAsJson('/oauth/device/code', {'client_id': CLIENT_ID})
        verification_url = (control.lang(32513) % result['verification_url']).encode('utf-8')
        user_code = (control.lang(32514) % result['user_code']).encode('utf-8')
        expires_in = int(result['expires_in'])
        device_code = result['device_code']
        interval = result['interval']
		
		
        # print ("TRAKT DEVICE CODE", device_code)
        # print ("TRAKT interval CODE", interval)
        # print ("TRAKT expires_in CODE", expires_in)
        progressDialog = control.progressDialog
        progressDialog.create('Trakt', verification_url, user_code)

        for i in range(0, expires_in):
            try:
                if progressDialog.iscanceled(): break
                time.sleep(1)
                if not float(i) % interval == 0: raise Exception()
                r = getTraktAsJson('/oauth/device/token', {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'code': device_code})
                if 'access_token' in r: break
            except:
                pass

        try: progressDialog.close()
        except: pass

        token, refresh = r['access_token'], r['refresh_token']

        headers = {'Content-Type': 'application/json', 'trakt-api-key': CLIENT_ID, 'trakt-api-version': '2', 'Authorization': 'Bearer %s' % token}


        result = requests.get(urlparse.urljoin(BASE_URL, '/users/me'), headers=headers).content
        result = utils.json_loads_as_str(result)

        user = result['username']
        control.infoDialog('Trakt Account Verified', sound=True, icon='INFO')
        control.setSetting(id='trakt.user', value=user)
        control.setSetting(id='trakt.token', value=token)
        control.setSetting(id='trakt.refresh', value=refresh)
        control.setSetting(id='indicators.alt', value='1')
        control.setSetting(id='trakt.scrobblePlayback', value='true')
        raise Exception()
    except:
        control.openSettings('3.1')


def getTraktCredentialsInfo():
    user = control.setting('trakt.user').strip()
    token = control.setting('trakt.token')
    refresh = control.setting('trakt.refresh')
    if user == '' or token == '' or refresh == '': return False
    return True


def getTraktIndicatorsInfo():
    if control.setting('indicators.alt') == '1': 
		if getTraktCredentialsInfo() == False: indicators = False
		else: indicators = True
		
    else: indicators = False
    return indicators


def getTraktAddonMovieInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_movie')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def getTraktAddonEpisodeInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_episode')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def manager(name, imdb, tvdb, content):
    try:
        post = {"movies": [{"ids": {"imdb": imdb}}]} if content == 'movie' else {"shows": [{"ids": {"tvdb": tvdb}}]}

        items = [(control.lang(32516).encode('utf-8'), '/sync/collection')]
        items += [(control.lang(32517).encode('utf-8'), '/sync/collection/remove')]
        items += [(control.lang(32518).encode('utf-8'), '/sync/watchlist')]
        items += [(control.lang(32519).encode('utf-8'), '/sync/watchlist/remove')]
        items += [(control.lang(32520).encode('utf-8'), '/users/me/lists/%s/items')]

        result = getTraktAsJson('/users/me/lists')
        lists = [(i['name'], i['ids']['slug']) for i in result]
        lists = [lists[i//2] for i in range(len(lists)*2)]
        for i in range(0, len(lists), 2):
            lists[i] = ((control.lang(32521) % lists[i][0]).encode('utf-8'), '/users/me/lists/%s/items' % lists[i][1])
        for i in range(1, len(lists), 2):
            lists[i] = ((control.lang(32522) % lists[i][0]).encode('utf-8'), '/users/me/lists/%s/items/remove' % lists[i][1])
        items += lists

        select = control.selectDialog([i[0] for i in items], control.lang(32515).encode('utf-8'))

        if select == -1:
            return
        elif select == 4:
            t = control.lang(32520).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            new = k.getText() if k.isConfirmed() else None
            if (new == None or new == ''): return
            result = __getTrakt('/users/me/lists', post={"name": new, "privacy": "private"})[0]

            try: slug = utils.json_loads_as_str(result)['ids']['slug']
            except: return control.infoDialog(control.lang(32515).encode('utf-8'), heading=str(name), sound=True, icon='ERROR')
            result = __getTrakt(items[select][1] % slug, post=post)[0]
        else:
            result = __getTrakt(items[select][1], post=post)[0]

        icon = control.infoLabel('ListItem.Icon') if not result == None else 'ERROR'

        control.infoDialog(control.lang(32515).encode('utf-8'), heading=str(name), sound=True, icon=icon)
    except:
        return


def slug(name):
    name = name.strip()
    name = name.lower()
    name = re.sub('[^a-z0-9_]', '-', name)
    name = re.sub('--+', '-', name)
    return name


def sort_list(sort_key, sort_direction, list_data):
    reverse = False if sort_direction == 'asc' else True
    if sort_key == 'rank':
        return sorted(list_data, key=lambda x: x['rank'], reverse=reverse)
    elif sort_key == 'added':
        return sorted(list_data, key=lambda x: x['listed_at'], reverse=reverse)
    elif sort_key == 'title':
        return sorted(list_data, key=lambda x: utils.title_key(x[x['type']].get('title')), reverse=reverse)
    elif sort_key == 'released':
        return sorted(list_data, key=lambda x: _released_key(x[x['type']]), reverse=reverse)
    elif sort_key == 'runtime':
        return sorted(list_data, key=lambda x: x[x['type']].get('runtime', 0), reverse=reverse)
    elif sort_key == 'popularity':
        return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
    elif sort_key == 'percentage':
        return sorted(list_data, key=lambda x: x[x['type']].get('rating', 0), reverse=reverse)
    elif sort_key == 'votes':
        return sorted(list_data, key=lambda x: x[x['type']].get('votes', 0), reverse=reverse)
    else:
        return list_data

def _released_key(item):
    if 'released' in item:
        return item['released']
    elif 'first_aired' in item:
        return item['first_aired']
    else:
        return 0

def getActivity():
    try:
        i = getTraktAsJson('/sync/last_activities')

        activity = []
        activity.append(i['movies']['collected_at'])
        activity.append(i['episodes']['collected_at'])
        activity.append(i['movies']['watchlisted_at'])
        activity.append(i['shows']['watchlisted_at'])
        activity.append(i['seasons']['watchlisted_at'])
        activity.append(i['episodes']['watchlisted_at'])
        activity.append(i['lists']['updated_at'])
        activity.append(i['lists']['liked_at'])
        activity = [int(cleandate.iso_2_utc(i)) for i in activity]
        activity = sorted(activity, key=int)[-1]

        return activity
    except:
        pass


def getWatchedActivity():
    try:
        i = getTraktAsJson('/sync/last_activities')

        activity = []
        activity.append(i['movies']['watched_at'])
        activity.append(i['episodes']['watched_at'])
        activity = [int(cleandate.iso_2_utc(i)) for i in activity]
        activity = sorted(activity, key=int)[-1]

        return activity
    except:
        pass


def cachesyncMovies(timeout=0):
    indicators = cache.get(syncMovies, timeout, control.setting('trakt.user').strip())
    return indicators


def timeoutsyncMovies():
    timeout = cache.timeout(syncMovies, control.setting('trakt.user').strip())
    return timeout


def syncMovies(user):
    try:
        if getTraktCredentialsInfo() == False: return
        indicators = getTraktAsJson('/users/me/watched/movies')
		
	
        indicators = [i['movie']['ids'] for i in indicators]
        indicators = [str(i['imdb']) for i in indicators if 'imdb' in i]
		
      
        return indicators
    except:
        pass


def cachesyncTVShows(timeout=0):
    indicators = cache.get(syncTVShows, timeout, control.setting('trakt.user').strip())
    return indicators
	

def timeoutsyncTVShows():
    timeout = cache.timeout(syncTVShows, control.setting('trakt.user').strip())
    return timeout
	
def cachesyncMoviesToLibrary():
    indicators = syncMoviesToLibrary(control.setting('trakt.user').strip())
    return indicators
	
	
def cachesyncTVShowsToLibrary():
    indicators = syncTVShowsToLibrary(control.setting('trakt.user').strip())
    return indicators
	
def syncMoviesToLibrary(user):
    try:
	
        if getTraktCredentialsInfo() == False: return

        indicators = getTraktAsJson('/sync/watched/movies')
		
        indicators = [(i['movie']['ids']['imdb'], i['movie']['ids']['tmdb'], i['plays']) for i in indicators]
        indicators = [(str(i[0]), str(i[1]), str(i[2])) for i in indicators]
        return indicators
    except:
        pass
	
def syncTVShowsToLibrary(user):
    try:

        if getTraktCredentialsInfo() == False: return

        indicators = getTraktAsJson('/sync/watched/shows')
		
        indicators = [(i['show']['ids']['tvdb'], sum([[(s['number'], e['number']) for e in s['episodes']] for s in i['seasons']], [])) for i in indicators]
        indicators = [(str(i[0]), i[1]) for i in indicators]
        return indicators
    except:
        pass


def syncTVShows(user):
    try:
        if getTraktCredentialsInfo() == False: return
        indicators = getTraktAsJson('/users/me/watched/shows?extended=full')
        indicators = [(i['show']['ids']['tvdb'], i['show']['aired_episodes'], sum([[(s['number'], e['number']) for e in s['episodes']] for s in i['seasons']], [])) for i in indicators]
        indicators = [(str(i[0]), int(i[1]), i[2]) for i in indicators]
        return indicators
    except:
        pass


def syncSeason(imdb):
    try:
        if getTraktCredentialsInfo() == False: return
        indicators = getTraktAsJson('/shows/%s/progress/watched?specials=false&hidden=false' % imdb)
        indicators = indicators['seasons']
        indicators = [(i['number'], [x['completed'] for x in i['episodes']]) for i in indicators]
        indicators = ['%01d' % int(i[0]) for i in indicators if not False in i[1]]
        return indicators
    except:
        pass


def markMovieAsWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return __getTrakt('/sync/history', {"movies": [{"ids": {"imdb": imdb}}]})[0]


def markMovieAsNotWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return __getTrakt('/sync/history/remove', {"movies": [{"ids": {"imdb": imdb}}]})[0]


def markTVShowAsWatched(tvdb):
    return __getTrakt('/sync/history', {"shows": [{"ids": {"tvdb": tvdb}}]})[0]


def markTVShowAsNotWatched(tvdb):
    return __getTrakt('/sync/history/remove', {"shows": [{"ids": {"tvdb": tvdb}}]})[0]


def markEpisodeAsWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return __getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})[0]


def markEpisodeAsNotWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return __getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})[0]


def getMovieTranslation(id, lang, full=False):
    url = '/movies/%s/translations/%s' % (id, lang)
    try:
        item = getTraktAsJson(url)[0]
        return item if full else item.get('title')
    except:
        pass


def getTVShowTranslation(id, lang, season=None, episode=None, full=False):
    if season and episode:
        url = '/shows/%s/seasons/%s/episodes/%s/translations/%s' % (id, season, episode, lang)
    else:
        url = '/shows/%s/translations/%s' % (id, lang)

    try:
        item = getTraktAsJson(url)[0]
        return item if full else item.get('title')
    except:
        pass


def getMovieAliases(id):
    try: return getTraktAsJson('/movies/%s/aliases' % id)
    except: return []


def getTVShowAliases(id):
    try: return getTraktAsJson('/shows/%s/aliases' % id)
    except: return []


def getMovieSummary(id, full=True):
    try:
        url = '/movies/%s' % id
        if full: url += '?extended=full'
        return getTraktAsJson(url)
    except:
        return


def getTVShowSummary(id, full=True):
    try:
        url = '/shows/%s' % id
        if full: url += '?extended=full'
        return getTraktAsJson(url)
    except:
        return


def getPeople(id, content_type, full=True):
    try:
        url = '/%s/%s/people' % (content_type, id)
        if full: url += '?extended=full'
        return getTraktAsJson(url)
    except:
        return

def SearchAll(title, year, full=True):
    try:
        return SearchMovie(title, year, full) + SearchTVShow(title, year, full)
    except:
        return

def SearchMovie(title, year, full=True):
    try:
        url = '/search/movie?query=%s' % title

        if year: url += '&year=%s' % year
        if full: url += '&extended=full'
        return getTraktAsJson(url)
    except:
        return

def SearchTVShow(title, year, full=True):
    try:
        url = '/search/show?query=%s' % title

        if year: url += '&year=%s' % year
        if full: url += '&extended=full'
        return getTraktAsJson(url)
    except:
        return

def IdLookup(content, type, type_id):
    try:
        r = getTraktAsJson('/search/%s/%s?type=%s' % (type, type_id, content))
        return r[0].get(content, {}).get('ids', [])
    except:
        return {}

def getGenre(content, type, type_id):
    try:
        r = '/search/%s/%s?type=%s&extended=full' % (type, type_id, content)
        r = getTraktAsJson(r)
        r = r[0].get(content, {}).get('genres', [])
        return r
    except:
        return []

		
def returnPlayback(type, imdb = None, tvdb = None, season = None, episode = None):
	try:
		if not imdb == None: imdb = str(imdb)
		if not tvdb == None: tvdb = int(tvdb)
		if not episode == None: episode = int(episode)
		if not season  == None: season = int(season)
		link = '/sync/playback/type'
		items = getTraktAsJson(link)
		if type == 'episode':
			if imdb:
				for item in items:
					if 'show' in item and 'imdb' in item['show']['ids'] and item['show']['ids']['imdb'] == imdb:
						if item['episode']['season'] == season and item['episode']['number'] == episode:
							return item['progress']
			elif tvdb:
				for item in items:
					if 'show' in item and 'tvdb' in item['show']['ids'] and item['show']['ids']['tvdb'] == tvdb:
						if item['episode']['season'] == season and item['episode']['number'] == episode:
		 					return item['progress']
		else:
			if imdb:
				for item in items:
					if 'movie' in item and 'imdb' in item['movie']['ids'] and item['movie']['ids']['imdb'] == imdb:
						return item['progress']
	except: return 0
	
def getPlayback(type):
	try:
		link = '/sync/playback/%s' % type
		items = getTraktAsJson(link)
		return items
	except: return 0
	
	
def removePlayback(id):
	try:
		link = '/sync/playback/%s' % id
		r = __getTrakt(link, method='delete')
		return items
	except: return 0

	
# action = start, pause, stop
# type =  episode, movie
# progress = 0-100

def scrobblePlayback(action, type, imdb = None, tvdb = None, season = None, episode = None, progress = 0):
	try:
		if action:
			if not imdb == None: imdb = str(imdb)
			if not tvdb == None: tvdb = int(tvdb)
			if not season == None: season = int(season)
			if not episode == None: episode = int(episode)
			if imdb: link = '/search/imdb/' + str(imdb)
			elif tvdb: link = '/search/tvdb/' + str(tvdb)
			if type == 'episode': link += '?type=show'
			else: link += '?type=movie'

			items = cache.get(getTraktAsJson, 720, link)

			if len(items) > 0:
				item = items[0]
				if type == 'episode':
					slug = item['show']['ids']['slug']
					link = '/shows/%s/seasons/%d/episodes/%d' % (slug, season, episode)
					item = cache.get(getTraktAsJson, 720, link)
				else:
					item = item['movie']

				if item:
					link = '/scrobble/' + action
					data = {type : item , 'progress' : progress}
					result = __getTrakt(link, post = data)
					return 'progress' in result
	except:
		return False
		
		