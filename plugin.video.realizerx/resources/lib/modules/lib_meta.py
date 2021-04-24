# -*- coding: utf-8 -*-

import re,sys,urllib.parse

RES_8K   = ['8k', 'hd8k','hd8k','8khd','8khd','4320p','4320i','hd4320','4320hd','4320p','4320i','hd4320','4320hd','5120p','5120i','hd5120','5120hd','5120p','5120i','hd5120','5120hd','8192p','8192i','hd8192','8192hd','8192p','8192i','hd8192','8192hd']
RES_6K   = ['6k','hd6k','hd6k','6khd','6khd','3160p','3160i','hd3160','3160hd','3160p','3160i','hd3160','3160hd','4096p','4096i','hd4096','4096hd','4096p','4096i','hd4096','4096hd']
RES_4K   = ['hd4k','hd4k','4khd','4khd','uhd','ultrahd','ultrahd','ultrahigh','2160','2160p','2160i','hd2160','2160hd','2160','2160p','2160i','hd2160','2160hd','1716p','1716i','hd1716','1716hd','1716p','1716i','hd1716','1716hd','2664p','2664i','hd2664','2664hd','2664p','2664i','hd2664','2664hd','3112p','3112i','hd3112','3112hd','3112p','3112i','hd3112','3112hd','2880p','2880i','hd2880','2880hd','2880p','2880i','hd2880','2880hd']
RES_2K   = ['1440p','1440i','1440','hd2k','hd2k','2khd','2khd','2048p','2048i','hd2048','2048hd','2048p','2048i','hd2048','2048hd','1332p','1332i','hd1332','1332hd','1332p','1332i','hd1332','1332hd','1556p','1556i','hd1556','1556hd','1556p','1556i','hd1556','1556hd',]

RES_1080 = ['1080','1080p','1080i','hd1080','1080hd','1080','1080p','1080i','hd1080','1080hd','1200p','1200i','hd1200','1200hd','1200p','1200i','hd1200','1200hd']
RES_HD   = ['720','720p','720i','hd720','720hd','hd','720','720p','720i','hd720','720hd']
FILTER_HD= ['hdtv' , 'hdts' , 'hdrip']

RES_SD   = ['576','576p','576i','sd576','576sd','576','576p','576i','sd576','576sd','480','480p','480i','sd480','480sd','480','480p','480i','sd480','480sd','360','360p','360i','sd360','360sd','360','360p','360i','sd360','360sd','240','240p','240i','sd240','240sd','240','240p','240i','sd240','240sd']
SCR      = ['dvdscr','screener','scr','r5','r6','dvdscr','r5','r6']
CAM      = ['camrip','camrip','tsrip','tsrip','hdcam','hdcam','hdts','hdts','dvdcam','dvdcam','dvdts','dvdts','cam','telesync','telesync','ts','camrip','tsrip','hdcam','hdts','dvdcam','dvdts','telesync']

CODEC_H265 = ['hevc','h265','x265','265','hevc','h265','x265']
CODEC_H264 = ['avc','h264','x264','264','h264','x264']
CODEC_XVID = ['xvid','xvid']
CODEC_DIVX = ['divx','divx','div2','div2','div3','div3']
CODEC_MPEG = ['mp4','mpeg','m4v','mpg','mpg1','mpg2','mpg3','mpg4','mp4','mpeg','msmpeg','msmpeg4','mpegurl','m4v','mpg','mpg1','mpg2','mpg3','mpg4','msmpeg','msmpeg4']
CODEC_AVI  = ['avi']
CODEC_MKV  = ['mkv','mkv','matroska','matroska']

AUDIO_8CH=['ch8','8ch','ch7','7ch','7.1','ch71','7.1ch','ch8','8ch','ch7','7ch','7 1']
AUDIO_6CH=['ch6','6ch','ch6','6ch','6.1','ch6.1','61ch','5 1','5.1','ch5.1','5.1ch','ch6','6ch','ch6','6ch']
AUDIO_2CH=['ch2','2ch','stereo','dualaudio','dual','2.1','2.0','ch20','20ch','ch2','2ch','stereo','dualaudio','dual']
AUDIO_1CH=['ch1','1ch','mono','monoaudio','ch10','10ch','ch1','1ch','mono']

VIDEO_3D=['3d','sbs','hsbs','sidebyside','sidebyside','stereoscopic','tab','htab','topandbottom','topandbottom']


#============================================== TORRENTS META ==================================================================    


def normalizeASCII(txt):
    txt = re.sub(r'[^\x00-\x7f]',r' ', txt)
    title = ' '.join(txt.split())
    return txt

def torrent_info(seeds=None, size=None, title=None):
    try:
        title = meta_info(title)
        if seeds != None and seeds != '': seeds = "S: " + str(seeds)
        info = [seeds, str(size), title]
        info = [i for i in info if i != None and i != '']
        info = ' | '.join(info)
        info = ' '.join(info.split())
        return info 
    except: return ''
    
#==============================================META QUALITY ==================================================================  

def meta_quality(txt):
    txt = txt.lower()
    if any(value in txt for value in RES_4K): quality = "4K"
    elif any(value in txt for value in RES_2K): quality = "2K"
    elif any(value in txt for value in RES_1080): quality = "1080p"
    
    elif any(value in txt for value in RES_HD): 
        quality = "HD"
        if any(value in txt for value in FILTER_HD):
            if "1080" in txt: quality = "1080p"
            elif "720" in txt: quality = "HD"
            else: quality = "SD"    
            
    else: quality = "SD"
    return quality  
    
def meta_quality_plus(txt, href):
    txt = txt.lower()
    if any(value in txt for value in RES_4K): quality = "4K"
    elif any(value in txt for value in RES_2K): quality = "2K"
    elif any(value in txt for value in RES_1080): quality = "1080p"
    
    elif any(value in txt for value in RES_HD): 
        quality = "HD"
        if any(value in txt for value in FILTER_HD):
            if "1080" in txt: quality = "1080p"
            elif "720" in txt: quality = "HD"
            else: quality = "SD"    
            
    else: quality = "SD"
    
    if quality == 'SD':
        if any(value in href for value in RES_4K): quality = "4K"
        elif any(value in href for value in RES_2K): quality = "2K"
        elif any(value in href for value in RES_1080): quality = "1080p"
        
        elif any(value in href for value in RES_HD): 
            quality = "HD"
            if any(value in href for value in FILTER_HD):
                if "1080" in href: quality = "1080p"
                elif "720" in href: quality = "HD"
                else: quality = "SD"    
                
        else: quality = "SD"    
    
    return quality  

    
    
# ============================================== META INFO  ==================================================================  



def meta_info(txt):
    txt = txt.lower()
    info = ''
    codec = get_codec(txt)
    audio = get_audio(txt)
    size = get_size(txt)
    video3d = get_3D(txt)   
    filetype = get_filetype(txt)
    info = size + " " + codec + " " + audio + " " + filetype + " " + video3d
    info = ' '.join(info.split())
    return info 

def get_codec(txt):
    txt = txt.lower()
    if any(value in txt for value in CODEC_H265): txt = "HEVC"
    elif any(value in txt for value in CODEC_MKV): txt = "MKV"
    elif any(value in txt for value in CODEC_DIVX): txt = "DIVX"
    elif any(value in txt for value in CODEC_MPEG): txt = "MPEG"
    elif any(value in txt for value in CODEC_XVID): txt = "XVID"
    elif any(value in txt for value in CODEC_AVI): txt = "AVI"
                
     
    else: txt = ''
    return txt
    
def get_audio(txt):
    try:
        txt = txt.lower()
        type = '' 
        if any(value in txt for value in AUDIO_8CH): type = " 7.1 "
        if any(value in txt for value in AUDIO_6CH): type = " 5.1 "
        if any(value in txt for value in AUDIO_2CH): type = " 2.0 "
        if any(value in txt for value in AUDIO_1CH): type = " Mono "
        return type
    except: return ''
    
def get_3D(txt):
    txt = txt.lower()
    if any(value in txt for value in VIDEO_3D): txt = "3D"
    else: txt = ''
    return txt
    
def get_size(txt):
    txt = txt.lower()
    try:
        txt = re.findall('(\d+(?:\.|/,|)?\d+(?:\s+|)(?:gb|GiB|mb|MiB|GB|MB))', txt)
        txt = txt[0].encode('utf-8')
        txt = txt
    except:
        txt = ''
    return txt

def getSizeFromBytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'B' if 0 == B > 1 else 'B')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)
      
      
def get_filetype(txt):

    try: txt = txt.lower()
    except: txt = str(txt)
    type = ''
    if 'hdtv' in txt: type += ' HDTV '   
    if 'bluray' in txt: type += ' BLURAY '
    if 'hdrip' in txt: type += ' HDRip '
    if 'web-dl' in txt or 'webdl' in txt: type += ' WEB-DL '
    if 'br-rip' in txt or 'brrip' in txt: type += ' BR-RIP '
    if 'bd-rip' in txt or 'bd-r' in txt or 'bdrip' in txt: type += ' BD-RIP '
    if 'atmos' in txt: type += ' ATMOS '
    if 'truehd' in txt: type += ' TRUEHD '
    if 'shaanig' in txt: type += ' SHAANIG '
    if 'yts' in txt or 'yify' in txt: type += ' YIFY '
    if 'rarbg' in txt: type += ' RARBG '
    if 'subs' in txt: 
        if type != '': type += ' - WITH SUBS'
        else: type = 'SUBS'
    return type
    
    
# ============================================== META GVIDEO ====================================================================
    
def meta_google(url):
    quality = re.compile('itag=(\d*)').findall(url)
    quality += re.compile('=m(\d*)$').findall(url)
    try:
        quality = quality[0]
    except:
        return []

    if quality in ['266', '272', '313']:
        return [{'quality': '4K', 'url': url}]
    if quality in ['264', '271']:
        return [{'quality': '2K', 'url': url}]
    if quality in ['37', '137', '299', '96', '248', '303', '46']:
        return [{'quality': '1080p', 'url': url}]
    elif quality in ['15', '22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
        return [{'quality': 'HD', 'url': url}]
    elif quality in ['35', '44', '59', '135', '244', '94']:
        return [{'quality': 'SD', 'url': url}]
    elif quality in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
        return [{'quality': 'SD', 'url': url}]
    elif quality in ['5', '6', '36', '83', '133', '242', '92', '132']:
        return [{'quality': 'SD', 'url': url}]
    else:
        return []   
    
    
    
def meta_gvideo_quality(url):
    quality = re.compile('itag=(\d*)').findall(url)
    quality += re.compile('=m(\d*)$').findall(url)
    try: 
        quality = quality[0]
    except:
        quality = "ND"
        return quality
    if quality in ['266', '272', '313']:
        quality = "4K"
    if quality in ['264', '271']:
        quality = "2K"
    if quality in ['37', '137', '299', '96', '248', '303', '46']:
        quality = "1080p"
        return quality
    elif quality in ['22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
        quality = "HD"
        return quality
    elif quality in ['35', '44', '135', '244', '94']:
        quality = "SD"
        return quality
    elif quality in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
        quality = "SD"
        return quality
    elif quality in ['5', '6', '36', '83', '133', '242', '92', '132']:
        quality = "SD"
        return quality
    else:
        quality = "SD"
        return quality


# ============================================== META HOST ====================================================================
        
def meta_host(url):
    try: 
        url = url.replace('\\','')
        host = url
        if host.startswith('http://'): host = host
        elif host.startswith('https://'): host = host
        elif host.startswith('//'): host = 'http:' + host
        else: host = 'http://' + host
        host = urllib.parse.urlparse(host).hostname
        host = host.replace('http:','')
        host = host.replace('https:','')
        host = host.replace('www.','')
        host = re.sub('[^A-z0-9.]', '', str(host))
        host = host.lower()
        host = ''.join(host.split())
        host = host[-30:]
    except: 
        print(("SOLARIS META UNKNOWN", url))
        host = 'unknown'
        
    return host

