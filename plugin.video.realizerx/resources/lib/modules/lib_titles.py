# -*- coding: utf-8 -*-

import re, unicodedata
from difflib import SequenceMatcher

# ========================= MATCH TITLES OR PORTIONS OF IT ===============================
def __matchClean(value):
	value = cleantitle_get(value)
	return value

def title_match(txt, txt2, amount=None):
	#print ("TITLEMATCH AMOUNT", amount)	
	if amount == None: MatchValue = 0.8
	else: MatchValue = amount
	value1 = __matchClean(txt)
	value2 = __matchClean(txt2)
	ratio_diff = SequenceMatcher(None, value1, value2).ratio()
	#print ("RATIO MATCHES ratio_diff", ratio_diff, value1, value2)
	if SequenceMatcher(None, value1, value2).ratio() >= MatchValue:
		#print ("RATIO MATCHES PASSED ", value1, value2)
		
		return True
	else:
			# Sometimes there are very long strings before or after the actual name, causing a non-match. Divide the string into 2 and check each part.
		split = -((-len(value1))//2)
		if SequenceMatcher(None, value1[:split], value2).ratio() >= MatchValue or SequenceMatcher(None, value1[split:], value2).ratio() >= MatchValue:
			#print ("RATIO MATCHES 2")
			return True
		else: return False

def normalize_string(text):
	try:
		norm_text = u'%s' % text
		norm_text = ''.join(c for c in unicodedata.normalize('NFD', norm_text) if unicodedata.category(c) != 'Mn')
		return norm_text
	except: return text


		
		
# ============================= TITLE CLEANS =========================================================


def cleantitle_get(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', '', title)
    title = re.sub('[^A-z0-9]', '', title)
    return title
	
	
	
def cleantitle_get_2(title):
   # #### KEEPS ROUND PARENTHESES CONTENT #####
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|([[].+?[]])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}|\s', '', title)
    title = re.sub('[^A-z0-9]', '', title)
    return title
	
def cleantitle_get_full(title):
   # #### KEEPS ALL PARENTHESES CONTENT #####
    if title == None: return
    title = title.lower()
    title = re.sub('(\d{4})', '', title)
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|\(|\)|\[|\]|\{|\}|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title)
    title = re.sub('[^A-z0-9]', '', title)
    return title
	
def cleantitle_geturl(title):
    if title == None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = title.replace('/', '-')
    title = title.replace(' ', '-')
    title = title.replace('--', '-')
    return title

def cleantitle_underscore(title):
    if title == None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = ' '.join(title.split())
    title = title.replace('/', '_')
    title = title.replace(' ', '_')
    title = title.replace('--', '_')
	
    return title
	
def cleantitle_get_simple(title):
    if title == None: return
    title = title.lower()
    title = re.sub('(\d{4})', '', title)
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub(r'\<[^>]*\>','', title)
    title = re.sub('\n|\(|\)|\[|\]|\{|\}|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title
	
def cleantitle_query(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|"|,|\'|\_|\.|\?|\!)|\(|\)|\[|\]|\{|\}', '', title)
    title = re.sub('-', ' ', title)
    title = ' '.join(title.split())
    title = title.lower()
    return title
	
def getsearch(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|"|,|\'|\_|\.|\?)|\(|\)|\[|\]|\{|\}', '', title)
    title = re.sub('-', ' ', title)
    title = ' '.join(title.split())
    title = title.lower()
    return title
	
def cleantitle_normalize(title):
    try:
        try: return title.decode('ascii').encode("utf-8")
        except: pass

        return str( ''.join(c for c in unicodedata.normalize('NFKD', unicode( title.decode('utf-8') )) if unicodedata.category(c) != 'Mn') )
    except:
        return title
		
def title_normalize(title):
	title = re.sub('(\d{4})', '', title)
	title = re.sub('&#(\d+);', '', title)
	title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
	title = title.replace('&quot;', '\"').replace('&amp;', '&')
	title = re.sub(r'\<[^>]*\>','', title)
	title = re.sub('\n|\t|\(|\)|\[|\]|\{|\}', '', title)
	title = ' '.join(title.split())
	return title
	
def clean_html(title):
	title = title.replace('&quot;', '\"').replace('&amp;', '&')
	title = title.replace('\\n','').replace('\\t','')
	title = title.replace('\\','')
	title = ' '.join(title.split())
	return title
	
	
def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.strip()
    return txt

def normalizeASCII(txt):
    txt = re.sub(r'[^\x00-\x7f]',r' ', txt)
    title = ' '.join(txt.split())
    return txt