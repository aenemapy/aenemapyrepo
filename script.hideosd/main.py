# -*- coding: utf-8 -*-

from urllib.parse import parse_qsl
import sys
params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

icon = params.get('icon')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

tmdb = params.get('tmdb')

trakt = params.get('trakt')

season = params.get('season')

episode = params.get('episode')

tvshowtitle = params.get('tvshowtitle')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

query = params.get('query')

source = params.get('source')

content = params.get('content')

if action == None:
    print("TODO MAIN ADDON SECTION")
