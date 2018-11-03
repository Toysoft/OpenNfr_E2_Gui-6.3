# -*- coding: utf-8 -*-
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
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper
from Plugins.Extensions.MediaPortal.additions.mediatheken.youtube import YT_ListScreen
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

default_cover = "file://%s/videogold_de.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class show_VGDE_Genre(MenuHelper):

	def __init__(self, session):
		baseUrl = "https://videogold.de"
		MenuHelper.__init__(self, session, 0, None, baseUrl, "", self._defaultlistcenter, default_cover=default_cover)

		self['title'] = Label("VideoGold.de")
		self['ContentTitle'] = Label("Genres")

		self.onLayoutFinish.append(self.mh_initMenu)

	def mh_parseCategorys(self, data):
		themes = ['Nach Format','Nach Thema']
		menu_marker = 'class="menu"'
		excludes = ['/livestreams','/videos-eintragen','/wp-login']
		menu=self.scanMenu(data,menu_marker,themes=themes,base_url=self.mh_baseUrl,url_ex=excludes)
		self.mh_genMenu2(menu)

	def mh_callGenreListScreen(self):
		genreurl = self.mh_genreUrl[self.mh_menuLevel].replace('&#038;','&')
		if not genreurl.startswith('https'):
			genreurl = self.mh_baseUrl+genreurl
		self.session.open(VGDE_FilmListeScreen, genreurl, self.mh_genreTitle)

class VGDE_FilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName):
		self.genreLink = genreLink
		self.genreName = genreName
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"0" : self.closeAll
		}, -1)

		self['title'] = Label("VideoGold.de")
		self['ContentTitle'] = Label(genreName)
		self['Page'] = Label(_("Page:"))

		self.filmQ = Queue.Queue(0)
		self.picQ = Queue.Queue(0)
		self.updateP = 0
		self.eventL = threading.Event()
		self.eventP = threading.Event()
		self.keyLocked = True
		self.dokusListe = []
		self.page = 1
		self.lastpage = 1

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)
		if '/?' in self.genreLink:
			self.genreLink = self.genreLink.replace('/?', '/seite/%d/?', 1)
		else:
			self.genreLink += "/seite/%d/"

	def loadPage(self):
		self.dokusListe = []
		self['handlung'].setText("")
		self.ml.setList(map(self._defaultlistleft, self.dokusListe))
		url = self.genreLink % max(self.page,1)
		self.filmQ.put(url)
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued()

	def loadPageQueued(self):
		self['name'].setText(_('Please wait...'))
		while not self.filmQ.empty():
			url = self.filmQ.get_nowait()
		twAgentGetPage(url, timeout=60).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		self.eventL.clear()
		printl(error,self,"E")
		if not 'TimeoutError' in str(error):
			message = self.session.open(MessageBoxExt, _("No dokus / streams found!"), MessageBoxExt.TYPE_INFO, timeout=5)
		else:
			message = self.session.open(MessageBoxExt, str(error), MessageBoxExt.TYPE_INFO)

	def loadPageData(self, data):
		for m in re.finditer('<article id=(.*?)</article>', data, re.S):
			m2 = re.search('<a href="(.*?)" title="(.*?)">.*?data-lazy-src="(.*?)".*?<p>(.*?)</p>', m.group(1), re.S)
			if m2:
				url, nm, img, desc = m2.groups()
				self.dokusListe.append((decodeHtml(nm), url, img, decodeHtml(desc)))
		if self.dokusListe:
			self.getLastPage(data, "class='wp-pagenavi'(.*?)</div>")

			self.ml.setList(map(self._defaultlistleft, self.dokusListe))
			self['liste'].moveToIndex(0)
			self.th_ThumbsQuery(self.dokusListe,0,1,2,None,None, self.page, self.lastpage, mode=1)
			self.loadPicQueued()
		else:
			self.dokusListe.append((_("No dokus found!"),"","",""))
			self.ml.setList(map(self._defaultlistleft, self.dokusListe))
			self['liste'].moveToIndex(0)
			if self.filmQ.empty():
				self.eventL.clear()
			else:
				self.loadPageQueued()

	def loadPic(self):
		if self.picQ.empty():
			self.eventP.clear()
			return
		if self.updateP:
			return
		while not self.picQ.empty():
			self.picQ.get_nowait()
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]
		self.updateP = 1
		CoverHelper(self['coverArt'], self.ShowCoverFileExit).getCover(streamPic)

	def getHandlung(self, desc):
		if desc == None:
			self['handlung'].setText(_("No further information available!"))
			return
		self.setHandlung(desc)

	def setHandlung(self, data):
		self['handlung'].setText(data)

	def ShowCoverFileExit(self):
		self.updateP = 0;
		self.keyLocked	= False
		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
			self.loadPic()

	def loadPicQueued(self):
		self.picQ.put(None)
		if not self.eventP.is_set():
			self.eventP.set()
		desc = self['liste'].getCurrent()[0][3]
		self.getHandlung(desc)
		self.loadPic()

	def parseYTStream(self, data):
		m2 = re.search('//www.youtube.*?com/(embed|v|p)/(.*?)(\?|" |&amp)', data)
		url = None
		if m2:
			dhVideoId = m2.group(2)
			if 'p' == m2.group(1):
				url = 'gdata.youtube.com/feeds/api/playlists/PL'+dhVideoId+'?'
		else:
			m2 = re.search('//youtu.be/(.*?)"', data)
			if m2:
				dhVideoId = m2.group(1)
		if m2:
			dhTitle = self['liste'].getCurrent()[0][0]
			if url:
				url = 'gdata.youtube.com/feeds/api/playlists/PL'+dhVideoId+'?'
				self.session.open(YT_ListScreen, url, dhTitle, title="videogold")
			else:
				self.session.open(YoutubePlayer, [(dhTitle, dhVideoId, None)], showPlaylist=False)

	def keyOK(self):
		if (self.keyLocked|self.eventL.is_set()):
			return
		streamLink = self['liste'].getCurrent()[0][1]
		twAgentGetPage(streamLink, timeout=60).addCallback(self.parseYTStream).addErrback(self.dataError)