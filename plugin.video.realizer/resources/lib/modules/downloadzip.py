import xbmcgui
import urllib
import time
start = time.time()
class customdownload(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

def silent_download(url, dest):
    customdownload().retrieve(url, dest)	

def download(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("","",' ', ' ')
    dp.update(0)
    start_time= time.time()
    customdownload().retrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb, bs, fs, dp, start_time))
	
def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100)
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
            e = 'Speed: %.02f Kb/s ' % kbps_speed 
            e += 'ETA: %02d:%02d' % divmod(eta, 60)
			
            end = time.time()

            elapsed = end - start
			
            
            string = '[COLOR Lime]Downloading... Please Wait...[/COLOR]'
            dp.update(percent, mbs, e)
        except Exception as e:
            percent = 100 
            print ("realizer DOWNLOADER ERROR", str(e))
            #dp.close() 
