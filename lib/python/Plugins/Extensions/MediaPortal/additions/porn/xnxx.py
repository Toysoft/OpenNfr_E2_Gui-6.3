# -*- coding: utf-8 -*-
#######################################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2019
#
#  This plugin is open source but it is NOT free software.
#
#  This plugin may only be distributed to and executed on hardware which
#  is licensed by Dream Property GmbH. This includes commercial distribution.
#  In other words:
#  It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
#  to hardware which is NOT licensed by Dream Property GmbH.
#  It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
#  on hardware which is NOT licensed by Dream Property GmbH.
#
#  This applies to the source code as a whole as well as to parts of it, unless explicitely
#  stated otherwise.
#
#  If you want to use or modify the code or parts of it, permission from the authors is necessary.
#  You have to keep OUR license and inform us about any modification, but it may NOT be distributed
#  other than under the conditions noted above.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#
#  For other uses, permission from the authors is necessary.
#
#######################################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt

agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
json_headers = {
	'Accept':'application/json',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/x-www-form-urlencoded',
	}
default_cover = "file://%s/xnxx.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding':'deflate, br',
	'Accept-Language':'en-US,en;q=0.9',
	'Host':'www.xnxx.com'
	}

class xnxxGenreScreen(MPScreen):

	def __init__(self, session, Link=None, Name=None):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("XNXX.com")
		if self.Name:
			self['ContentTitle'] = Label("Genre: %s" % self.Name)
		else:
			self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		if self.Link:
			self.url = self.Link
		else:
			self.url = "https://www.xnxx.com/tags/"
		twAgentGetPage(self.url, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		if self.Name:
			parse = re.search('id="best-months">(.*?)$', data, re.S)
			Cats = re.findall('<a href="(/best/.*?)"\s+(?:class="hidden"|)>(.*?)</a>', parse.group(1), re.S)
			if Cats:
				for (Url, Title) in Cats:
					Url = "https://www.xnxx.com" + Url + "/$$PAGE$$"
					self.filmliste.append((Title, Url, default_cover, False))
		else:
			parse = re.search('id="tags">(.*?)$', data, re.S)
			if parse:
				Cats = re.findall('<li><a href="(/tags/.*?)">(.*?)</a><strong>(.*?)</strong></li>', parse.group(1), re.S)
				if Cats:
					for (Url, Title, Count) in Cats:
						Count = int(Count.replace(',',''))
						if Count > 250:
							Url = "https://www.xnxx.com" + Url + "/$$PAGE$$/"
							self.filmliste.append((Title.title(), Url, default_cover, False))
			self.filmliste.sort()
			self.filmliste.insert(0, ("Best Of", "https://www.xnxx.com/best", default_cover, False))
			self.filmliste.insert(0, ("Most Popular", "https://www.xnxx.com/home/$$PAGE$$", default_cover, False))
			self.filmliste.insert(0, ("Most Viewed", "https://www.xnxx.com/hits/$$AGE$$$$PAGE$$", default_cover, True))
			self.filmliste.insert(0, ("--- Search ---", "callSuchen", default_cover, True))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		cover = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(cover)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Filter =	 self['liste'].getCurrent()[0][3]
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		elif Name == "Best Of":
			self.session.open(xnxxGenreScreen, Link, Name)
		elif self.Name and self.Name.endswith("Best Of"):
			self.session.open(xnxxFilmScreen, Link, Name, Best=True, Filter=Filter)
		else:
			self.session.open(xnxxFilmScreen, Link, Name, Filter=Filter)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(xnxxFilmScreen, Link, Name)

	def getSuggestions(self, text, max_res):
		url = "https://www.xnxx.com/search-suggest/%s" % urllib.quote_plus(text)
		d = twAgentGetPage(url, agent=agent, headers=json_headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions["KEYWORDS"]:
				li = item['N']
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class xnxxFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Related=False, Best=False, Filter=True):
		self.Link = Link
		self.Name = Name
		self.Related = Related
		self.Best = Best
		self.Filter = Filter
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber,
			"yellow" : self.keyRelated,
			"blue" : self.keyAge
		}, -1)

		self['title'] = Label("XNXX.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		if self.Filter and not self.Related and not self.Best and self.Name != "Most Popular":
			self['F4'].setText(_("Filter"))
		self['F3'] = Label(_("Show Related"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if re.match(".*Search", self.Name):
			self.age = ''
			self.agename = 'All time'
		elif self.Filter:
			self.age = ''
			self.agename = 'All time'
		else:
			self.age = ''
			self.agename = ''
		self.keywords = False

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if self.Related:
			twAgentGetPage(self.Link, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)
		else:
			if re.match(".*Search", self.Name):
				url = "https://www.xnxx.com/search/%s%s/%s/" % (self.age, self.Link, str(self.page-1))
			else:
				url = self.Link.replace('$$PAGE$$', str(self.page-1)).replace('$$AGE$$', self.age)
			print url
			twAgentGetPage(url, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		if self.Related:
			self['page'].setText('1 / 1')
			datarel = re.findall('var video_related=(.*?);window.wpn_categories', data, re.S)
			if datarel:
				json_data = json.loads(datarel[0])
				for item in json_data:
					Title = str(item["tf"])
					Url = "https://www.xnxx.com" + str(item["u"])
					Image = str(item["i"])
					Runtime = str(item["d"])
					Views = str(item["n"])
					Rating = str(item["r"])
					if Rating == "? %":
						Rating = "-"
					self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views, Rating))
		else:
			self.getLastPage(data, 'class="pagination(.*?)</div>')
			Movies = re.findall('id="video_\d+"\sclass="thumb-block\s{0,1}">.*?class="thumb"><a href="(.*?)"><img src=".*?data-src="(.*?)".*?<a href.*?title="(.*?)">.*?</a></p><p class="metadata">(.*?)</div>', data, re.S)
			if Movies:
				for (Url, Image, Title, Meta) in Movies:
					Metadata = re.findall('<span class="right">(?:\s(.*?)\s<span class="icon-f icf-eye"></span>|)(?:<span class="superfluous">(.*?)</span>|)</span>\s(.*?)\s<span class="video-hd">', Meta, re.S)
					if Metadata:
						if Metadata[0][0]:
							Views = Metadata[0][0]
						else:
							Views = "-"
						if Metadata[0][1]:
							Rating = Metadata[0][1]
						else:
							Rating = "-"
						Runtime = Metadata[0][2]
					Url = "https://www.xnxx.com" + Url
					Image = Image.replace('img-hw.xnxx-cdn', 'img-egc.xnxx-cdn').replace('thumbs169/', 'thumbs169lll/').replace('thumbs169ll/', 'thumbs169lll/').replace('THUMBNUM.jpg', '15.jpg')
					self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views, Rating))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), "", None, None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def keyRelated(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(xnxxFilmScreen, Link, "Related", Related=True)

	def keyAge(self):
		if self.keyLocked:
			return
		elif self.Name == "Most Popular":
			return
		elif not self.Filter:
			return
		if self.Related or self.Best:
			return
		if re.match(".*Search", self.Name):
			rangelist = [ ['Today', 'day/'], ['Yesterday', 'yesterday/'], ['2 days ago', '2daysago/'], ['This week', 'week/'], ['This month', 'month/'], ['All time', ''] ]
		elif self.Name == "Most Viewed":
			rangelist = [ ['Today', 'day/'], ['This week', 'week/'], ['This month', 'month/'], ['All time', ''] ]
		else:
			rangelist = [ ['Today', 'day/'], ['Yesterday', 'yesterday/'], ['2 days ago', '2daysago/'], ['This week', 'week/'], ['This month', 'month/'], ['All time', ''] ]
		self.session.openWithCallback(self.keyAgeAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyAgeAction(self, result):
		if result:
			self.age = result[1]
			self.agename = result[0]
			self.loadPage()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		rating = self['liste'].getCurrent()[0][5]
		self['name'].setText(title)
		if self.agename and self.Name != "Most Popular" and not self.Best and not self.Related:
			agename = "\n%s: %s" % (_("Filter"), self.agename)
		else:
			agename = ''
		self['handlung'].setText("Runtime: %s\nViews: %s\nRating: %s%s" % (runtime, views, rating, agename))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			twAgentGetPage(Link, agent=agent, headers=headers).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		match = re.findall("setVideo(?:UrlLow|UrlHigh|HLS)\('(.*?)'\);", data)
		if match:
			url = match[-1].replace('\/','/').replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
			if "/hls/" in url:
				#if len(url.split('hls.m3u8')[1]) > 0:
				baseurl = url.split('hls.m3u8')[0]
				twAgentGetPage(url, agent=agent).addCallback(self.loadplaylist, baseurl).addErrback(self.dataError)
				#else:
				#	if len(match)>1:
				#		url = match[-2].replace('\/','/').replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
				#		self.playVideo(url)
				#	else:
				#		message = self.session.open(MessageBoxExt, _("Stream not found"), MessageBoxExt.TYPE_INFO, timeout=5)
			else:
				self.playVideo(url)
		else:
			message = self.session.open(MessageBoxExt, _("Stream not found"), MessageBoxExt.TYPE_INFO, timeout=5)

	def loadplaylist(self, data, baseurl):
		self.bandwith_list = []
		match_sec_m3u8=re.findall('BANDWIDTH=(\d+).*?\n(.*?m3u8.*?)\n', data, re.S)
		max = 0
		for x in match_sec_m3u8:
			if int(x[0]) > max:
				max = int(x[0])
		videoPrio = int(config_mp.mediaportal.videoquali_others.value)
		if videoPrio == 2:
			bw = max
		elif videoPrio == 1:
			bw = max/2
		else:
			bw = max/3
		for each in match_sec_m3u8:
			bandwith,url = each
			self.bandwith_list.append((int(bandwith),url))
		_, best = min((abs(int(x[0]) - bw), x) for x in self.bandwith_list)
		url = baseurl.replace('https','http') + best[1]
		playlist_path = config_mp.mediaportal.storagepath.value+"tmp.m3u8"
		f1 = open(playlist_path, 'w')
		f1.write('#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1\n%s' % url)
		f1.close()
		self.playVideo("file://%stmp.m3u8" % config_mp.mediaportal.storagepath.value)

	def playVideo(self, url):
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='xnxx')