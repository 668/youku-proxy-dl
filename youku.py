#!/usr/bin/python

import json
import os
import random
import re
import subprocess
import sys
import urllib.request

class ChinaProxy(object):
	def __init__(self):
		self.get_list()

	def get_list(self):
		print('[proxy] Downloading proxy list')
		request_object = urllib.request.Request('http://letushide.com/export/json/http,all,cn/',
			headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
		proxy_list = urllib.request.urlopen(request_object)
		proxy_array = json.loads(proxy_list.read().decode('utf-8'))

		proxies = []
		for proxy in proxy_array:
			proxies.append(proxy['host'] + ':' + proxy['port'])

		print('[proxy] Proxies downloaded, found {}'.format(len(proxies)))
		self.proxy_list = proxies

	def use(self):
		if len(self.proxy_list) == 0:
			print('[proxy] Proxy list empty')
			self.get_list()
		random.seed()
		random_proxy = self.proxy_list.pop(random.randrange(0, len(self.proxy_list)-1))

		print('[proxy] Picking {}'.format(random_proxy))
		return random_proxy

def download_video(url, proxy):
	arglist = ['/usr/local/bin/youtube-dl', '-o', os.getcwd() + '/%(id)s.%(ext)s', '--proxy', proxy, url]

	p = subprocess.Popen(arglist)
	p.wait()
	return p.returncode

def concat_video(video_id):
	print('[concat] Looking for files')
	directory_listing = os.listdir(path=os.getcwd())
	video_files = []
	for filename in directory_listing:
		if re.search(video_id, filename):
			video_files.append(filename)

	if len(video_files) == 0:
		print('[concat] No files found. Aborting...')
		return False

	print('[concat] Found {} files to concatenate'.format(str(len(video_files))))

	with open('videolist.txt', 'w') as f:
		for video in video_files:
			f.write("file '" + video + "'\n")

	print('[concat] Starting concatenation')
	arglist = ['/usr/local/bin/ffmpeg', '-f', 'concat', '-i', 'videolist.txt', '-c', 'copy', video_id + '.flv']
	p = subprocess.Popen(arglist, stderr=open(os.devnull, 'wb'))
	p.wait()
	print(p.returncode)
	print('[concat] Concatenation complete. Output: {}'.format(video_id + '.flv'))

	os.remove('videolist.txt')
	for video in video_files:
		os.remove(video)

urls = sys.argv[1:]
proxies = ChinaProxy()

for url in urls:
	proxy = proxies.use()
	video_id = re.search(r'.*id_(.*)\.html', url).group(1)
	returncode = download_video(url, proxy)
	while(returncode != 0):
		returncode = download_video(url, proxy)
		if returncode != 0:
			proxy = proxies.use()
	
	concat_video(video_id)
