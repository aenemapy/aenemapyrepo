# -*- coding: utf-8 -*-

'''
realizer TIMER
'''
import time
import datetime
from resources.lib.modules import control
timerEndOffset = int(control.setting('scrapers.timer.offset'))
timerChecksOffset = int(control.setting('scrapers.timer.check.offset'))
timerEnd =  int(control.setting('scrapers.timeout.1')) - timerEndOffset
timerChecks =  int(control.setting('scrapers.timeout.1')) - timerChecksOffset
timerEnabled =  control.setting('scrapers.timer')

print ("SCRAPER TIMERS", timerEnd, timerChecks)
class Time(object):

	# Use time.clock() instead of time.time() for processing time.
	# NB: Do not use time.clock(). Gives the wrong answer in timestamp() AND runs very fast in Linux. Hence, in the stream finding dialog, for every real second, Linux progresses 5-6 seconds.
	# http://stackoverflow.com/questions/85451/python-time-clock-vs-time-time-accuracy
	# https://www.tutorialspoint.com/python/time_clock.htm

	ZoneUtc = 'utc'
	ZoneLocal = 'local'

	def __init__(self, start = False):
		self.mStart = None		
		if start: 
			self.start()
			print ("TIMER TIME STARTED")

	def start(self):
		self.mStart = time.time()
		return self.mStart

	def stop(self):
		self.mStart = 0
		return self.mStart		
		
	def restart(self):
		return self.start()

	def elapsed(self, milliseconds = False):
		if self.mStart == None:
			self.mStart = time.time()
		if milliseconds: return int((time.time() - self.mStart) * 1000)
		else: return int(time.time() - self.mStart)

	def expired(self, expiration):
		return self.elapsed() >= expiration

	def isExpired(self):
		if timerEnabled == 'false': return False
		if self.elapsed() > timerEnd: return True
		else: return False
		
	def checkExpired(self):
		if timerEnabled == 'false': return False
		if self.elapsed() > timerChecks: return True
		else: return False
		
	@classmethod
	def sleep(self, seconds):
		time.sleep(seconds)

	# UTC timestamp
	@classmethod
	def timestamp(self, fixedTime = None):
		if fixedTime == None:
			# Do not use time.clock(), gives incorrect result for search.py
			return int(time.time())
		else:
			return int(time.mktime(fixedTime.timetuple()))

	# datetime object from string
	@classmethod
	def datetime(self, string, format = '%Y-%m-%d %H:%M:%S'):
		try:
			return datetime.datetime.strptime(string, format)
		except:
			# Older Kodi Python versions do not have the strptime function.
			# http://forum.kodi.tv/showthread.php?tid=112916
			return datetime.datetime.fromtimestamp(time.mktime(time.strptime(string, format)))