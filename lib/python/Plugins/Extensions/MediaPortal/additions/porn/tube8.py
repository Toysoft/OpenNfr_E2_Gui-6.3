﻿# -*- coding: utf-8 -*-
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

agent='Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
json_headers = {
	'Accept':'application/json',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/json',
	}
default_cover = "file://%s/tube8.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class tube8GenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"yellow" : self.keyScope
		}, -1)

		self.scope = 0
		self.scopeText = ['Straight', 'Shemale', 'Gay']
		self.scopeval = ['', 'shemale/', 'gay/']

		self['title'] = Label("Tube8.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['F3'].setText(self.scopeText[self.scope])
		self.url = "http://www.tube8.com/%scategories.html" % self.scopeval[self.scope]
		getPage(self.url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('id="porn-categories-box" class="gridList"(.*?)</ul>', data,re.S)
		Cats = re.findall('a\shref="(http[s]?://www.tube8.com/%scat/.*?)">.*?data-thumb="(.*?)".*?<h5>(.*?)<span>' % self.scopeval[self.scope], parse.group(1), re.S)
		if Cats:
			for (Url, Image, Title) in Cats:
				Url = Url + "page/"
				self.filmliste.append((Title, Url, Image))
		self.filmliste.sort()
		self.filmliste.insert(0, ("Longest", "http://www.tube8.com/%slongest/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Most Voted", "http://www.tube8.com/%smost-voted/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Most Discussed", "http://www.tube8.com/%smost-discussed/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Most Favorited", "http://www.tube8.com/%smost-favorited/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Top Rated", "http://www.tube8.com/%stop/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Most Popular", "http://www.tube8.com/%shottest/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Most Viewed", "http://www.tube8.com/%smost-viewed/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Featured", "http://www.tube8.com/%slatest/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("Newest", "http://www.tube8.com/%snewest/page/" % self.scopeval[self.scope], default_cover))
		self.filmliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
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
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(tube8FilmScreen, Link, Name)

	def keyScope(self):
		if self.keyLocked:
			return
		self.filmliste = []
		if self.scope == 0:
			self.scope = 1
		elif self.scope == 1:
			self.scope = 2
		else:
			self.scope = 0
		self.layoutFinished()

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '%20')
			self.session.open(tube8FilmScreen, Link, Name, Scope=self.scopeval[self.scope][:-1])

	def getSuggestions(self, text, max_res):
		if self.scopeval[self.scope][:-1] == '':
			scope = 'straight'
		else:
			scope = self.scopeval[self.scope][:-1]
		url = "https://bnzmzkcxit-dsn.algolia.net/1/indexes/popular_queries_" + scope + "_de/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.32.0&x-algolia-application-id=BNZMZKCXIT&x-algolia-api-key=3624454cb0b8c87da7f6100dde6ce062"
		postdata = {'params':'query='+text}
		postdata = json.dumps(postdata)
		d = twAgentGetPage(url, method='POST', postdata=postdata, agent=agent, headers=json_headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions['hits']:
				li = item['query']
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class tube8FilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Scope=''):
		self.Link = Link
		self.Name = Name
		if Scope == '':
			self.Scope = 'straight'
		else:
			self.Scope = Scope
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
			"blue" : self.keyFilter
		}, -1)

		self['title'] = Label("Tube8.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Sort"))
		self['F4'] = Label(_("Filter"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if re.match(".*Search", self.Name):
			self.sort = ''
			self.sortsearch = 'tube8_slave_relevance'
			self.sortname = 'Relevance'
		else:
			self.sort = 'lt'
			self.sortsearch = 'tube8_slave_featured'
			self.sortname = 'Featured'
		self.filter = None
		self.filtersearch = ''
		self.filtername = 'Any Duration'

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*Search", self.Name):
			url = "https://bnzmzkcxit-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser&x-algolia-application-id=BNZMZKCXIT&x-algolia-api-key=3624454cb0b8c87da7f6100dde6ce062"
			postdata = '{"requests":[{"indexName":"' + self.sortsearch + '","params":"query=' + self.Link + '&optionalWords=null&facetFilters=%5B%22attributes.orientation%3A' + self.Scope + '%22' + self.filtersearch + '%5D&facets=*&page=' + str(self.page-1) +'&hitsPerPage=19"}]}'
			getPage(url, method='POST', agent=agent, postdata=postdata, headers={'Content-Type': 'application/x-www-form-urlencoded'}).addCallback(self.genreData).addErrback(self.dataError)
		else:
			if self.page == 1:
				url = self.Link.replace('page/','')
			else:
				url = "%s%s/" % (self.Link, str(self.page))
			if self.sort:
				url = "%s?orderby=%s" % (url, self.sort)
			if self.filter:
				url = ("%s?filter_duration=%s" % (url, self.filter)).replace('?', '&').replace('&', '?', 1)
			getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		if re.match(".*Search", self.Name):
			results = json.loads(data)
			if results:
				self.lastpage = int(results["results"][0]["nbPages"])
				self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
				for node in results["results"][0]["hits"]:
					Url = str(node["link"])
					Image = str(node["thumbnails"][0]["urls"][0])
					Title = str(node["title"])
					Seconds = int(node["attributes"]["durationInSeconds"])
					m, s = divmod(Seconds, 60)
					Runtime = "%02d:%02d" % (m, s)
					Views = str(node["attributes"]["stats"]["views"])
					self.filmliste.append((Title, Url, Image, Runtime, Views))
		else:
			self.getLastPage(data, 'id="pagination"(.*?)</ul>')
			preparse = re.search('id="category_video_list"(.*?)$', data, re.S)
			Movies = re.findall('id="video_i\d+.*?href="(.*?)".*?data-thumb="(http[s]?://.*?\.jpg)".*?title="(.*?)".*?(class="video-attributes-features">.*?video-likes)', preparse.group(1), re.S)
			if Movies:
				for (Url, Image, Title, Meta) in Movies:
					Metadata = re.findall('video-duration">(.*?)</span.*?video-views"></span><span>(.*?)</span', Meta, re.S)
					Runtime = Metadata[0][0]
					Views = Metadata[0][1]
					self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views.strip()))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), "", None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, 999, mode=1)
		self.showInfos()

	def keySort(self):
		if self.keyLocked:
			return
		rangelist = [ ['Featured', 'lt', 'tube8_slave_featured'], ['Longest', 'ln', 'tube8_slave_longest'], ['Newest', 'nt', 'tube8_slave_newest'], ['Rating', 'tr', 'tube8_slave_rating'], ['Views', 'mv', 'tube8_slave_views'], ['Hottest', 'rl', 'tube8_slave_magic'], ['Votes', 'mt', 'tube8_slave_votes'], ['Comments', 'md', 'tube8_slave_comments'], ['Favorites', 'mf', 'tube8_slave_favorites']]
		if re.match(".*Search", self.Name):
			rangelist.insert(0,['Relevance', '', 'tube8_slave_relevance'])
		self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keySortAction(self, result):
		if result:
			self.sort = result[1]
			self.sortsearch = result[2]
			self.sortname = result[0]
			self.loadPage()

	def keyFilter(self):
		if self.keyLocked:
			return
		rangelist = [['Any Duration', '', ''], ['Short 0-5 Min', 'short', '%2C%22attributes.durationInSeconds_round%3A1%22'], ['Medium 5-20 Min', 'medium', '%2C%22attributes.durationInSeconds_round%3A2%22'], ['Long 20+ Min', 'long', '%2C%22attributes.durationInSeconds_round%3A3%22']]
		self.session.openWithCallback(self.keyFilterAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyFilterAction(self, result):
		if result:
			self.filter = result[1]
			self.filtersearch = result[2]
			self.filtername = result[0]
			self.loadPage()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s\nViews: %s\n%s: %s\n%s: %s" % (runtime, views, _("Sort order"), self.sortname, _("Filter"), self.filtername))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		getPage(Link).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		Title = self['liste'].getCurrent()[0][0]
		match = re.findall('"quality_\d+p":"(http.*?)"', data)
		if match:
			url = match[-1].replace('\/','/').replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='tube8')
		else:
			message = self.session.open(MessageBoxExt, _("Stream not found"), MessageBoxExt.TYPE_INFO, timeout=5)