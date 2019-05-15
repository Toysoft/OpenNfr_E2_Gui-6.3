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
import requests

agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
default_cover = "file://%s/spankbang.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
json_headers = {
	'Accept':'application/json',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/x-www-form-urlencoded',
	}
cookies = CookieJar()
ck = {}

class spankbangGenreScreen(MPScreen):

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

		self['title'] = Label("SpankBang.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		ck.update({'language':'www'})
		requests.cookies.cookiejar_from_dict(ck, cookiejar=cookies)
		self.keyLocked = True
		url = "https://spankbang.com/categories"
		twAgentGetPage(url, agent=agent, cookieJar=cookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="categories">(.*?)</div>', data, re.S)
		if parse:
			Cats = re.findall('<a\shref="(.*?)"><img\ssrc="(.*?)"><span>(.*?)</span', parse.group(1), re.S)
			if Cats:
				for (Url, Image, Title) in Cats:
					if "?" in Url:
						Url = Url.split('?')[0]
					Url = "https://spankbang.com" + Url
					Image = "https://spankbang.com" + Image
					self.filmliste.append((Title, Url, Image, False, False, True))
		self.filmliste.sort()
		self.filmliste.insert(0, ("Longest", "https://spankbang.com/longest_videos/", default_cover, False, True, False))
		self.filmliste.insert(0, ("Trending", "https://spankbang.com/trending_videos/", default_cover, False, False, False))
		self.filmliste.insert(0, ("Upcoming", "https://spankbang.com/upcoming/", default_cover, False, False, False))
		self.filmliste.insert(0, ("Interesting", "https://spankbang.com/interesting/", default_cover, False, True, False))
		self.filmliste.insert(0, ("Top Rated", "https://spankbang.com/top_rated/", default_cover, False, True, False))
		self.filmliste.insert(0, ("Most Popular", "https://spankbang.com/most_popular/", default_cover, False, True, False))
		self.filmliste.insert(0, ("Newest", "https://spankbang.com/new_videos/", default_cover, False, False, False))
		self.filmliste.insert(0, ("--- Search ---", "callSuchen", default_cover, True, True, False))
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
		Age = self['liste'].getCurrent()[0][4]
		Cat = self['liste'].getCurrent()[0][5]
		if Name == "--- Search ---":
			self.suchen()
		else:
			self.session.open(spankbangFilmScreen, Link, Name, Sort, Age, Cat)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(spankbangFilmScreen, Link, Name, True, True)

class spankbangFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Sort, Age=False, Cat=False):
		self.Link = Link
		self.Name = Name
		self.Sort = Sort
		self.Age = Age
		self.Cat = Cat
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
			"yellow" : self.keySort,
			"blue" : self.keyAge
		}, -1)

		self['title'] = Label("SpankBang.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		if self.Sort or self.Cat:
			self['F3'] = Label(_("Sort"))
		if self.Age:
			self['F4'].setText(_("Filter"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if re.match(".*Search", self.Name):
			self.sortname = 'Relevance'
			self.sort = 'order='
			self.age = 'period=all'
			self.agename = 'All time'
		else:
			if self.Cat:
				self.sortname = 'New'
				self.sort = 'order=all'
			else:
				self.sortname = ''
				self.sort = ''
			if self.Age:
				self.age = 'period=all'
				self.agename = 'All time'
			else:
				self.age = ''
				self.agename = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*Search", self.Name):
			url = "https://spankbang.com/s/%s/%s/?%s&%s" % (self.Link, str(self.page), self.sort, self.age)
		else:
			url = self.Link + "%s/?%s&%s" % (str(self.page), self.sort, self.age)
		twAgentGetPage(url, agent=agent, cookieJar=cookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		self.getLastPage(data, 'class="pagination">(.*?)</ul>')
		parse = re.search('class="results(.*?)$', data, re.S)
		Movies = re.findall('class="video-item".*?href="(.*?)".*?data-src="(.*?)"\salt="(.*?)".*?class="stats".*?fa-eye"></i>\s(.*?)\s.*?fa-thumbs-o-up"></i>\s(.*?)\s.*?<span>(.*?)</span', parse.group(1), re.S)
		if Movies:
			for (Url, Image, Title, Views, Rating, Age) in Movies:
				Url = "https://spankbang.com" + Url
				if Image.startswith('//'):
					Image = "http:" + Image
				self.filmliste.append((decodeHtml(Title), Url, Image, Rating, Views, Age))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), "", None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def keySort(self):
		if self.keyLocked:
			return
		if self.Cat:
			rangelist = [ ['Trending', 'order=trending'], ['Upcoming', 'order=upcoming'], ['Interesting', 'order=interesting'], ['New', 'order=all'], ['Popular', 'order=popular'], ['Most liked', 'order=rated'], ['Longest', 'order=length'] ]
			self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)
		elif self.Sort:
			rangelist = [ ['Relevance', 'order='], ['Popular', 'order=top'], ['New', 'order=new'], ['Most liked', 'order=hot'] ]
			self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)


	def keySortAction(self, result):
		if result:
			self.sort = result[1]
			self.sortname = result[0]
			self.loadPage()

	def keyAge(self):
		if self.keyLocked:
			return
		if self.Age:
			rangelist = [ ['All time', 'period=all'], ['Today', 'period=today'], ['This week', 'period=week'], ['This month', 'period=month'], ['Three months', 'period=season'], ['This year', 'period=year'] ]
			self.session.openWithCallback(self.keyAgeAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyAgeAction(self, result):
		if result:
			self.age = result[1]
			self.agename = result[0]
			self.loadPage()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		rating = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		age = self['liste'].getCurrent()[0][5]
		self['name'].setText(title)
		if self.agename:
			agename = "\n%s: %s" % (_("Filter"), self.agename)
		else:
			agename = ''
		if self.sortname:
			sort = "\n%s: %s" % (_("Sort order"), self.sortname)
		else:
			sort = ''
		self['handlung'].setText("Rating: %s\nViews: %s\nAge: %s%s%s" % (rating, views, age, agename, sort))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		twAgentGetPage(Link, cookieJar=cookies, agent=agent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		match = re.findall('data-streamkey="(.*?)"', data, re.S)
		if match:
			postdata = {'id': match[0]}
			url = "https://spankbang.com/api/videos/stream"
			if 'id="vr_player"' in data:
				vr = True
			else:
				vr = False
			twAgentGetPage(url, method='POST', postdata=urlencode(postdata), cookieJar=cookies, agent=agent, headers=json_headers).addCallback(self.parseVideo, vr).addErrback(self.dataError)

	def parseVideo(self, data, vr):
		if vr:
			resolutions = "720|480|320|240"
		else:
			resolutions = "1080|720|480|320|240"
		streams = re.findall('stream_url_(%s)p":"(.*?)"' % resolutions, data, re.S)
		if streams:
			vidres = 0
			for (res, url) in streams:
				if int(res) > vidres and len(url) > 0:
					vidres = int(res)
					vidurl = url
			Title = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(Title, vidurl)], showPlaylist=False, ltype='spankbang')