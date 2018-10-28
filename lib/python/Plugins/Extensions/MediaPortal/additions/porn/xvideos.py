﻿# -*- coding: utf-8 -*-
#############################################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2018
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
#  This applies to the source code as a whole as well as to parts of it, unless
#  explicitely stated otherwise.
#
#  If you want to use or modify the code or parts of it,
#  you have to keep OUR license and inform us about the modifications, but it may NOT be
#  commercially distributed other than under the conditions noted above.
#
#  As an exception regarding execution on hardware, you are permitted to execute this plugin on VU+ hardware
#  which is licensed by satco europe GmbH, if the VTi image is used on that hardware.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#  For other uses, permission from the authors is necessary.
#
#############################################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.decrypt import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt

agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
json_headers = {
	'Accept':'application/json',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/x-www-form-urlencoded',
	}
default_cover = "file://%s/xvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding':'deflate, br',
	'Accept-Language':'en-US,en;q=0.9',
	'Host':'www.xvideos.com'
	}

class xvideosGenreScreen(MPScreen):

	def __init__(self, session):
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

		self['title'] = Label("XVideos.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.url = "https://www.xvideos.com/lang"
		twAgentGetPage(self.url, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="dyn.*?href="/c/(.*?)">(.*?)</a', data, re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = "https://www.xvideos.com/c/$$AGE$$$$PAGE$$/" + Url
				self.filmliste.append((Title, Url, default_cover, False))
		Cats = re.findall('li><a href="/lang/(.*?)"\stitle="(.*?)"', data, re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = "https://www.xvideos.com/porn/" + Url + "/$$PAGE$$"
				self.filmliste.append((Title, Url, default_cover, False))
		self.filmliste.sort()

		self.filmliste.insert(0, ("Pornstars", "https://www.xvideos.com/pornstars-index/$$AGE$$$$PAGE$$", default_cover, False))
		self.filmliste.insert(0, ("100% Verified", "https://www.xvideos.com/verified/videos/$$PAGE$$", default_cover, False))
		self.filmliste.insert(0, ("Newest", "https://www.xvideos.com/new/$$PAGE$$", default_cover, False))
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
		Sort = self['liste'].getCurrent()[0][3]
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		elif Name == "Pornstars":
			self.session.open(xvideosPornstarsScreen, Link, Name, Sort)
		else:
			self.session.open(xvideosFilmScreen, Link, Name, Sort)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = self.suchString.replace(' ', '+')
			self.session.open(xvideosFilmScreen, Link, Name, True)

	def getSuggestions(self, text, max_res):
		url = "https://www.xvideos.com/search-suggest/%s" % urllib.quote_plus(text)
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

class xvideosPornstarsScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Sort):
		self.Link = Link
		self.Name = Name
		self.Sort = Sort
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
			"blue" : self.keyAge
		}, -1)

		self['title'] = Label("XVideos.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F4'] = Label(_("Filter"))
		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.age = ''
		self.agename = '1 Month'

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		url = self.Link.replace('$$PAGE$$', str(self.page-1)).replace('$$AGE$$', self.age)
		twAgentGetPage(url, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		lastp = re.search('label">.*?Top\s(.*?)\spornstars', data, re.S)
		if lastp:
			lastp = lastp.group(1).replace(',','')
			lastp = round((float(lastp) / 100) + 0.5)
			self.lastpage = int(lastp)
			self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		else:
			self.lastpage = 999
			self['page'].setText(str(self.page))
		Movies = re.findall('class="thumb"><a href="(.*?)">.*?<img src="(.*?)".*?class="flag(.*?)</p></div>', data, re.S)
		if Movies:
			for (Url, Image, Meta) in Movies:
				Title = re.findall('class="profile-name">.*?<a href=".*?">(.*?)</a>', Meta, re.S)
				if Title:
					Title = Title[0]
				else:
					Title = "---"
				Url = "https://www.xvideos.com" + Url + "/videos/$$PORNSTAR$$/$$PAGE$$"
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No pornstars found!'), "", None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def keyAge(self):
		if self.keyLocked:
			return
		rangelist = [ ['Ever', 'ever/'], ['1 Year', ''], ['3 Months', '3months/'], ['New', 'new/'] ]
		self.session.openWithCallback(self.keyAgeAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyAgeAction(self, result):
		if result:
			self.age = result[1]
			self.agename = result[0]
			self.loadPage()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		self['handlung'].setText("%s: %s" % (_("Filter"), self.agename))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(xvideosFilmScreen, Link, Name, False)

class xvideosFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Sort, Related=False):
		self.Link = Link
		self.Name = Name
		self.Sort = Sort
		self.Related = Related
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
			"red" : self.keyKeywords,
			"green" : self.keyPageNumber,
			"yellow" : self.keySortRelated,
			"blue" : self.keyAge
		}, -1)

		self['title'] = Label("XVideos.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		if self.Sort:
			self['F3'] = Label(_("Sort"))
			self['F4'].setText(_("Filter"))
		elif not self.Related and not self.Sort and self.Name != "Newest" and self.Name != "100% Verified" and not "Porn in" in self.Name and not "$$PORNSTAR$$" in self.Link:
			self['F4'].setText(_("Filter"))
		if not self.Sort:
			self['F3'] = Label(_("Show Related"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if re.match(".*Search", self.Name):
			self.sortname = 'Relevance'
			self.sort = 'relevance'
			self.age = 'all'
			self.agename = 'All time'
		else:
			self.sortname = 'Newest'
			self.sort = ''
			self.age = ''
			self.agename = 'All time'
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
			self.counter = 0
			twAgentGetPage(self.Link, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)
		else:
			if re.match(".*Search", self.Name):
				url = "https://www.xvideos.com/?k=%s&p=%s&sort=%s&datef=%s&durf=allduration&typef=straight" % (self.Link, str(self.page-1), self.sort, self.age)
			else:
				if self.page == 1 and self.Name == "Newest":
					url = self.Link.replace('/new/$$PAGE$$', '')
				elif self.page == 1 and "Porn in" in self.Name:
					url = self.Link.replace('$$PAGE$$', '')
				else:
					url = self.Link.replace('$$PAGE$$', str(self.page-1)).replace('$$AGE$$', self.age)
			self.counter = 1
			self.url2 = None
			if "$$PORNSTAR$$" in url:
				self.counter = 2
				self.url2 = url.replace('$$PORNSTAR$$', 'best')
				url = url.replace('$$PORNSTAR$$', 'pornstar')
				twAgentGetPage(self.url2, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)
			twAgentGetPage(url, agent=agent, headers=headers).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		if self.Related:
			self['page'].setText('1 / 1')
			datarel = re.findall('var video_related=(.*?);window.wpn_categories', data, re.S)
			if datarel:
				json_data = json.loads(datarel[0])
				for item in json_data:
					Title = str(item["t"])
					Url = "https://www.xvideos.com" + str(item["u"])
					Image = str(item["i"])
					Runtime = str(item["d"])
					Views = str(item["n"])
					self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views))
		else:
			self.keyword_list = []
			if re.match(".*Search", self.Name):
				keydata = re.search('Related searches</strong>(.*?)</div', data, re.S)
				if keydata:
					keywords = re.findall('<a href="/\?k=(.*?)&amp;related">(.*?)</a>', keydata.group(1), re.S)
					if keywords:
						for keyword in keywords:
							self.keyword_list.append([keyword[1], keyword[0]])
							self['F1'].setText(_("Keywords"))
							self.keywords = True
					else:
						self['F1'].setText("")
						self.keywords = False
				else:
					self['F1'].setText("")
					self.keywords = False
			self.counter -= 1
			lastp = re.search('(\d+,{0,1}\d+)\sverified women and couple videos', data, re.S)
			if lastp:
				lastp = lastp.group(1).replace(',','')
				lastp = round((float(lastp) / 24) + 0.5)
				self.lastpage = int(lastp)
				self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
			else:
				lastp = re.search('class="sub">\((.*?)\sresults\)</span>', data, re.S)
				if lastp:
					lastp = lastp.group(1).replace(',','').replace('+','')
					lastp = round((float(lastp) / 24) + 0.5)
					self.lastpage = int(lastp)
					self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
				else:
					lastp = re.search('current">(.*?)\svideos', data, re.S)
					if lastp:
						lastp = lastp.group(1).replace(',','')
						lastp = round((float(lastp) / 24) + 0.5)
						self.lastpage = int(lastp)
						self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
					else:
						self.lastpage = 999
						self['page'].setText(str(self.page))
			Movies = re.findall('id="video_\d+"\sclass="thumb-block\s{0,1}">.*?class="thumb"><a href="(.*?)"><img src=".*?data-src="(.*?)".*?<a href.*?title="(.*?)">.*?</a></p><p class="metadata">(.*?)</div>', data, re.S)
			if Movies:
				for (Url, Image, Title, Meta) in Movies:
					Views = re.findall('<span>\s-\s(.*?)\sViews</span>', Meta, re.S)
					if Views:
						Views = Views[0]
					else:
						Views = "0"
					Runtime = re.findall('class="duration">(.*?)</span>', Meta, re.S)
					if Runtime:
						Runtime = Runtime[0]
					else:
						Runtime = "-"
					Url = "https://www.xvideos.com" + Url
					Image = Image.replace('img-hw.xvideos-cdn', 'img-egc.xvideos-cdn').replace('thumbs169', 'thumbs169lll').replace('THUMBNUM.jpg', '15.jpg')
					self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views))
		if self.counter == 0:
			if len(self.filmliste) == 0:
				self.filmliste.append((_('No movies found!'), "", None, None, None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
			self.showInfos()

	def keyKeywords(self):
		if self.keyLocked:
			return
		if not self.keywords:
			return
		self.session.openWithCallback(self.keyKeywordsAction, ChoiceBoxExt, title=_('Select Action'), list = self.keyword_list)

	def keyKeywordsAction(self, result):
		if result:
			self.Link = result[1]
			self.loadPage()

	def keySortRelated(self):
		if self.keyLocked:
			return
		if self.Sort:
			rangelist = [ ['Relevance', 'relevance'], ['Upload date', 'uploaddate'], ['Rating', 'rating'], ['Length', 'length'], ['Views', 'views'] ]
			self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(xvideosFilmScreen, Link, "Related", False, True)

	def keySortAction(self, result):
		if result:
			self.sort = result[1]
			self.sortname = result[0]
			self.loadPage()

	def keyAge(self):
		if self.keyLocked:
			return
		elif not self.Sort and (self.Name == "Newest" or self.Name == "100% Verified" or "Porn in" in self.Name or "$$PORNSTAR$$" in self.Link):
			return
		if self.Related:
			return
		if re.match(".*Search", self.Name):
			rangelist = [ ['Today', 'today'], ['This week', 'week'], ['This month', 'month'], ['Last 3 month', '3month'], ['Last 6 month', '6month'], ['All time', 'all'] ]
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
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s\nViews: %s\n%s: %s\n%s: %s" % (runtime, views, _("Sort order"), self.sortname, _("Filter"), self.agename))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		twAgentGetPage(Link, agent=agent, headers=headers).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		match = re.findall("setVideo(?:UrlLow|UrlHigh|HLS)\('(.*?)'\);", data)
		if match:
			url = match[-1].replace('\/','/').replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
			if "/hls/" in url:
				if len(url.split('hls.m3u8')[1]) > 0:
					baseurl = url.split('hls.m3u8')[0]
					twAgentGetPage(url, agent=agent).addCallback(self.loadplaylist, baseurl).addErrback(self.dataError)
				else:
					if len(match)>1:
						url = match[-2].replace('\/','/').replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
						self.playVideo(url)
					else:
						message = self.session.open(MessageBoxExt, _("Stream not found"), MessageBoxExt.TYPE_INFO, timeout=5)
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
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='xvideos')