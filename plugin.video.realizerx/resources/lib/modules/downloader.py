# CREDITS TO MUCKY DUCK FOR THE DOWNLOADER MODULE

import xbmcgui
import urllib.request, urllib.parse, urllib.error
import time
import requests
import sys
import os
start = time.time()
from resources.lib.modules import control

def download(name, url):
    dataPath = control.setting('download.path')
    if dataPath == '' or dataPath == None: 
        control.infoDialog('Download Location is Empty...')
        return
    dest = os.path.join(dataPath, name)
    dp = None
    with open(dest, 'wb') as f:
        start = time.time()
        r = requests.get(url, stream=True)
        content_length = int(r.headers.get('content-length'))
        if content_length is None: f.write(r.content)
        else:
            dl = 0
            progress = 0
            for chunk in r.iter_content(512 * 1024):
                dl += len(chunk)
                if chunk: f.write(chunk)
                progress = (100 * dl / content_length)
                byte_speed = dl / (time.time() - start)
                kbps_speed = byte_speed / 1024
                mbps_speed = kbps_speed / 1024
                downloaded = float(dl) / (1024 * 1024)
                file_size = float(content_length) / (1024 * 1024)
                if byte_speed > 0:
                    eta = (content_length - dl) / byte_speed
                else:
                    eta = 0
                  
                output = "DOWNLOADING: %.1f MB of %.1f MB @ %.1f Mbps [ETA: %02d:%02d]" % (downloaded, file_size, mbps_speed, divmod(eta, 60)[0],divmod(eta, 60)[1])
             
                if not dp:
                    dp = control.progressDialog
                    dp.create('Downloading', output)
                if dp.iscanceled(): 
                    dp.close()
                    break
                dp.update(int(progress), output)
            #print('')
    try: dp.close()
    except:pass


