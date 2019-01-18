import re
import urllib
import urllib2
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import os
import inspect
import datetime, json, sys
from resources.lib.modules import control
try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

import time
import requests
start = time.time()

class downloader(object):
	def __init__(self):
		self.stopped = False	

	def stop_download(self):
		self.stopped = True	
	
	def getResponse(self, url, headers, size):
		try:
			if size > 0:
				size = int(size)
				headers['Range'] = 'bytes=%d-' % size

			req = urllib2.Request(url, headers=headers)

			resp = urllib2.urlopen(req, timeout=30)
			return resp
		except:
			return None
			
	def download(self, name, url):
		if url == None: return
		dest = control.setting('download.path')
		if dest == '' or dest == None: control.infoDialog('Download Location is Empty...')
		self.stopped = False

		image = control.icon

		try: headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
		except: headers = dict('')


		content = re.compile('(.+?)\sS(\d*)E\d*$').findall(name)
		transname = name.translate(None, '\/:*?"<>|').strip('.')
		transname = os.path.splitext(transname)[0]


		dest = control.transPath(dest)
		control.makeFile(dest)
		dest = os.path.join(dest, transname)
		control.makeFile(dest)

		dest = os.path.join(dest, name)

		sysheaders = urllib.quote_plus(json.dumps(headers))

		sysurl = urllib.quote_plus(url)

		systitle = urllib.quote_plus(name)

		sysimage = urllib.quote_plus(image)

		sysdest = urllib.quote_plus(dest)

		#script = inspect.getfile(inspect.currentframe())

		try:
			self.doDownload(url, dest, transname, image, headers)
			if self.stopped == True: control.infoDialog(transname, 'Download Stopped...')
			else: control.infoDialog(transname, 'Download Completed...')

		except Exception as e: 
			control.infoDialog('Unable to Download...')
			print ("realizer DOWNLOADER ERROR:", str(e))
		
	def logDownload(self, title, percent, url, mode='add'):

		control.makeFile(control.dataPath)
		DBFile = control.logDownloads
		newData = []
		dupes   = []

		timeNow =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
		download_data = {}
		
		try:  # PREPARE AND SET DB SOURCES
			dbcon = database.connect(DBFile)
			dbcur = dbcon.cursor()
		except:pass		
	
		try: # CREATE DB
			dbcur.execute("CREATE TABLE IF NOT EXISTS downloads (""title TEXT, ""percent TEXT, ""status TEXT, ""url TEXT)")
		except:
			pass				
			
		if mode == 'add' or mode == 'update':
			try:
				status = 'running'
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()	
				try:
					dbcur.execute("SELECT * FROM downloads WHERE title = '%s'" % (title))
					match = dbcur.fetchone()
					if len(match) > 0:
						print ("FOUND MATCH DATABASE", match[2])
						status = match[2]
						dbcur.execute("DELETE FROM downloads WHERE title = '%s'" % (title))
				except:pass
				dbcur.execute("INSERT INTO downloads Values (?, ?, ?, ?)", (title, str(percent), 'running', url))
				dbcon.commit()
				
			except Exception as e:
				print ("DATABASE ERROR", str(e))
			
		elif mode == 'get':
			try:
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()	
				try:
					dbcur.execute("SELECT * FROM downloads")
					match = dbcur.fetchall()
					return match
				except:pass
				
			except Exception as e:
				print ("DATABASE ERROR", str(e))
				
		elif mode == 'stop':
			try:
				status = 'stopped'
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()
				dbcur.execute("SELECT * FROM downloads WHERE title = '%s'" % (title))
				match = dbcur.fetchone()
				url = match[3]
					
				dbcur.execute("DELETE FROM downloads WHERE title = '%s'" % (title))
				dbcur.execute("INSERT INTO downloads Values (?, ?, ?, ?)", (title, str(percent), 'stopped', url))
				dbcon.commit()
				
			except Exception as e:
				print ("DATABASE ERROR", str(e))
					
		elif mode == 'delete':
			try:
				status = 'delete'
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()
				try:
					dbcur.execute("SELECT * FROM downloads WHERE title = '%s'" % (title))
					match = dbcur.fetchall()
					for item in match:
						loc = item[3]
						try: os.remove(loc)
						except:pass
						
					dbcur.execute("DELETE FROM downloads WHERE title = '%s'" % (title))
					dbcon.commit()					
				except:pass
				
			except Exception as e:
				print ("DATABASE ERROR", str(e))
					
		elif mode == 'status':
			try:
				status = 'new'
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()	
				try:
					dbcur.execute("SELECT * FROM downloads WHERE title = '%s'" % (title))
					match = dbcur.fetchone()
					if len(match) > 0:
						status = match[2]
						return status
				except: return 'new'
			except: return 'new'
			
		elif mode == 'completed':
			try:
				status = 'completed'
				dbcon = database.connect(DBFile)
				dbcur = dbcon.cursor()
				dbcur.execute("DELETE FROM downloads WHERE title = '%s'" % (title))
				dbcur.execute("INSERT INTO downloads Values (?, ?, ?, ?)", (title, '100', 'completed', url))
				dbcon.commit()
				
			except Exception as e:
				print ("DATABASE ERROR", str(e))
				

	def download_manager(self):
		sysaddon = sys.argv[0]
		syshandle = int(sys.argv[1])

		artPath = control.artPath() 
		addonFanart = control.addonFanart()
		
		DBFile = control.logDownloads
		newData = []
		dupes   = []
		cm = []
		thumb = 'cloud.png'
		thumb = control.getIcon(thumb)
		url = '%s?action=refresh' % (sysaddon)
		item = control.item(label='Refresh')
		item.addContextMenuItems(cm)
		item.setArt({'icon': thumb, 'thumb': thumb})
		if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
		control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)	

		
		data = self.logDownload('title', '0', '0', mode='get')

		for x in data:
				try:
					thumb = 'cloud.png'
					thumb = control.getIcon(thumb)
					cm = []

					percent = str(x[1]) + '%'
					title = x[0]
					status = x[2]
					u = x[3]
					if status == 'running' : status = '[B][[COLOR orange]Running[/COLOR]][/B]'
					elif status == 'stopped': status = '[B][[COLOR red]Stopped[/COLOR]][/B]'
					elif status == 'completed': status = '[B][[COLOR lime]Completed[/COLOR]][/B]'
					label = '[B][%s][/B] %s %s' % (percent, status, title)
					cm.append(('Stop Download', 'RunPlugin(%s?action=download_manager_stop&title=%s)' % (sysaddon, title)))
					cm.append(('Delete Download', 'RunPlugin(%s?action=download_manager_delete&title=%s)' % (sysaddon, title)))
					url = ''
					item = control.item(label=label)
					item.addContextMenuItems(items=cm, replaceItems=True)
					item.setArt({'icon': thumb, 'thumb': thumb})
					if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
					control.addItem(handle=syshandle, url=u, listitem=item, isFolder=False)
				except:pass
		
		control.content(syshandle, 'addons')
		control.directory(syshandle, cacheToDisc=False)

	def done(self, title, dest, downloaded):
	
		playing = xbmc.Player().isPlaying()

		text = xbmcgui.Window(10000).getProperty('GEN-DOWNLOADED')

		if len(text) > 0:
			text += '[CR]'

		if downloaded:
			text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR forestgreen]Download succeeded[/COLOR]')
		else:
			text += '%s : %s' % (dest.rsplit(os.sep)[-1], '[COLOR red]Download failed[/COLOR]')

		xbmcgui.Window(10000).setProperty('GEN-DOWNLOADED', text)

		if (not downloaded) or (not playing): 
			xbmcgui.Dialog().ok(title, text)
			xbmcgui.Window(10000).clearProperty('GEN-DOWNLOADED')

		
	def doDownload(self, url, dest, title, image, headers):
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

		url = urllib.unquote_plus(url)

		title = urllib.unquote_plus(title)

		image = urllib.unquote_plus(image)

		dest = urllib.unquote_plus(dest)

		file = dest.rsplit(os.sep, 1)[-1]

		resp = self.getResponse(url, headers, 0)

		if not resp:
			xbmcgui.Dialog().ok(title, dest, 'Download failed', 'No response from server')
			return

		try:    content = int(resp.headers['Content-Length'])
		except: content = 0

		try:    resumable = 'bytes' in resp.headers['Accept-Ranges'].lower()
		except: resumable = False

		print "Download Header"
		print resp.headers
		if resumable:
			print "Download is resumable"

		if content < 1:
			xbmcgui.Dialog().ok(title, file, 'Unknown filesize', 'Unable to download')
			return

		size = 1024 * 1024
		mb   = content / (1024 * 1024)

		if content < size:
			size = content

		total   = 0
		notify  = 0
		errors  = 0
		count   = 0
		resume  = 0
		sleep   = 0
		stopped = True
		if xbmcgui.Dialog().yesno(title + ' - Confirm Download', file, 'Complete file is %dMB' % mb, 'Continue with download?', 'Confirm',  'Cancel') == 1:
			return

		print 'Download File Size : %dMB %s ' % (mb, dest)

		#f = open(dest, mode='wb')
		f = xbmcvfs.File(dest, 'w')

		chunk  = None
		chunks = []
		
		self.logDownload(title, '0', dest, mode='add')
		xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( title, 'DOWNLOAD STARTED', 10000, image))
		while True:
			self.stopped = False
			downloaded = total
			for c in chunks:
				downloaded += len(c)
			percent = min(100 * downloaded / content, 100)
			if percent >= notify:
				# label = '[%s] %s MB of %s MB' % (str(percent)+ '%', downloaded / 1000000, content / 1000000)
				# xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( title + ' - In Progress - ' + str(percent)+ '%', label, 10000, image))

				print 'Download percent : %s %s %dMB downloaded : %sMB File Size : %sMB' % (str(percent)+'%', dest, mb, downloaded / 1000000, content / 1000000)

				notify += 1
				self.logDownload(title, percent, dest, mode='update')
			status = self.logDownload(title, '0', dest, mode='status')
			if status == 'stopped': 
				self.stopped = True
				break
			
			

			chunk = None
			error = False

			try:        
				chunk  = resp.read(size)
				if not chunk:
					if percent < 99:
						error = True
					else:
						while len(chunks) > 0:
							c = chunks.pop(0)
							f.write(c)
							del c

							
						# DOWNLOAD COMPLETED
						self.logDownload(title, '100', dest, mode='completed')
						f.close()
						print '%s download complete' % (dest)
						return self.done(title, dest, True)

			except Exception, e:
				print str(e)
				error = True
				sleep = 10
				errno = 0

				if hasattr(e, 'errno'):
					errno = e.errno

				if errno == 10035: # 'A non-blocking socket operation could not be completed immediately'
					pass

				if errno == 10054: #'An existing connection was forcibly closed by the remote host'
					errors = 10 #force resume
					sleep  = 30

				if errno == 11001: # 'getaddrinfo failed'
					errors = 10 #force resume
					sleep  = 30

			if chunk:
				errors = 0
				chunks.append(chunk)
				if len(chunks) > 5:
					c = chunks.pop(0)
					f.write(c)
					total += len(c)
					del c

			if error:
				errors += 1
				count  += 1
				print '%d Error(s) whilst downloading %s' % (count, dest)
				xbmc.sleep(sleep*1000)

			if (resumable and errors > 0) or errors >= 10:
				if (not resumable and resume >= 50) or resume >= 500:
					#Give up!
					print '%s download canceled - too many error whilst downloading' % (dest)
					return self.done(title, dest, False)

				resume += 1
				errors  = 0
				if resumable:
					chunks  = []
					#create new response
					print 'Download resumed (%d) %s' % (resume, dest)
					resp = self.getResponse(url, headers, total)
				else:
					#use existing response
					pass
					


class customdownload(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

def silent_download(url, dest):
    customdownload().retrieve(url, dest)	

def downloadZip(url, dest, name, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("realizer Downloader","Downloading: " + str(name),' ', ' ')
    dp.update(0)
    start_time= time.time()
    customdownload().retrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb, bs, fs, dp, name, start_time))
	
def _pbhook(numblocks, blocksize, filesize, dp, name, start_time):
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
            line1 = "Downloading: " + str(name)
            line2 = mbs
            line3 = e
            dp.update(percent, line1, line2, line3)
        except Exception as e:
            try: dp.close()
            except:pass
            percent = 100 
            print ("realizer DOWNLOADER ERROR", str(e))
        if dp.iscanceled(): 
			raise Exception("Canceled")
			try: dp.close()
			except:pass
			try: dp.close()
			except:pass
