# -*- coding: utf-8 -*-

"""
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
"""

import re
import unicodedata


def normalizeLibrary(title):
	title = re.sub('(\d{4})', '', title)
	title = re.sub('&#(\d+);', '', title)
	title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
	title = title.replace('&quot;', '\"').replace('&amp;', '&')
	title = re.sub(r'\<[^>]*\>','', title)
	title = re.sub('\\\|:|;|"|,|\'|\_|\.|\?|\!|\+|\=|\*|\/|\(|\)|\[|\]|\{|\}', '', title)
	title = re.sub('\_|\n|\t|\(|\)|\[|\]|\{|\}\"|\'|\"', '', title)
	title = ' '.join(title.split())
	return title	


def get(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', '', title)
    title = re.sub('[^A-z0-9]', '', title)
    return title


def geturl(title):
    if title is None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = title.replace('/', '-')
    title = title.replace(' ', '-')
    title = title.replace('--', '-')
    return title


def get_simple(title):
    if title is None: return
    title = title.lower()
    title = re.sub('(\d{4})', '', title)
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|\(|\)|\[|\]|\{|\}|\s(vs|v[.])\s|(:|;|-|–|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


def getsearch(title):
    if title is None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|-|–|:|;|\*|\?|"|\'|<|>|\|', '', title).lower()
    return title


def query(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|\(|\)|\[|\]|\{|\}|\?|\!', '', title)
    title = re.sub('\:|(;|"|,|\'|\.|\_|\-)', ' ', title)
    title = ' '.join(title.split())
    title = title.lower()
    return title


def normalize(title):
    try:
        try: return title.decode('ascii').encode("utf-8")
        except: pass

        return str(''.join(c for c in unicodedata.normalize('NFKD', unicode(title.decode('utf-8'))) if unicodedata.category(c) != 'Mn'))
    except:
        return title