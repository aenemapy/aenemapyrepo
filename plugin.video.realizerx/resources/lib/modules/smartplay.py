import re,sys,json,time,xbmc, urllib.request, urllib.parse, urllib.error

def scrape_next_episode(tvshowtitle, year, imdb, tvdb, lang, season=None, episode=None):

    from resources.lib.sources import sources
    from resources.lib.indexers import episodes
    
    title = tvshowtitle
    
    next_episode = episodes.seasons().tvdb_list(tvshowtitle, year, imdb, tvdb, 'en', limit='nextepisode', season=season, episode=episode)

    premiered     = next_episode[0]['premiered']
    new_season    = next_episode[0]['season']
    new_episode   = next_episode[0]['episode']
    meta = []
    select = '3'
        
    sources().smartplay(title, year, imdb, tvdb, '0', new_season, new_episode, tvshowtitle, premiered, '', autoplay=False, background=True)
    return next_episode[0]
    
def next_episode(tvshowtitle, year, imdb, tvdb, lang, season=None, episode=None):
    from resources.lib.indexers import episodes
    title = tvshowtitle
    next_episode = episodes.seasons().tvdb_list(tvshowtitle, year, imdb, tvdb, 'en', limit='nextepisode', season=season, episode=episode)
    return next_episode[0]
    
def play_next_episode(episode):
    time.sleep(3)
    while xbmc.getCondVisibility("Window.IsVisible(yesnodialog)") or xbmc.getCondVisibility("Window.IsVisible(busydialog)") or xbmc.getCondVisibility("Window.IsVisible(okdialog)"):
        time.sleep(1)

    item = episode

    from resources.lib.modules import control
    
    try: icon = item['poster']
    except: icon = control.addonIcon()
    title = item['title']
    year = item['year']
    imdb = item['imdb']
    tvdb = item['tvdb']
    tmdb = '0'
    season = item['season']
    episode = item['episode']
    tvshowtitle = item['tvshowtitle']
    premiered   = item['premiered']
    meta = item
    smartPlayMode = True
    select = control.setting('hosts.mode')
    sysmeta = urllib.parse.quote_plus(json.dumps(meta))
    systitle = urllib.parse.quote_plus(item['title'])
    systvshowtitle = urllib.parse.quote_plus(item['tvshowtitle'])
    syspremiered = urllib.parse.quote_plus(item['premiered'])
    sysaddon = sys.argv[0]
    
    control.infoDialog('Playing Next Episode...', tvshowtitle, icon=icon, time=3000)
    time.sleep(2)
    url = 'RunPlugin(%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s)' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta)
    control.execute(url)
    #sources().play(title, year, imdb, tvdb, '0', season, episode, tvshowtitle, premiered, item, select)
    #sources.sources().play(title, year, imdb, tvdb, tmdb, season, episode, tvshowtitle, premiered, meta, select)
    


