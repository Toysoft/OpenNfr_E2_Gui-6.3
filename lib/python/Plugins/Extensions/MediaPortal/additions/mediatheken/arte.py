# -*- coding: utf-8 -*-
###############################################################################################
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
###############################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
default_cover = "file://%s/arte.png" % (config.mediaportal.iconcachepath.value + "logos")

class arteFirstScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("arte Mediathek")
		self['ContentTitle'] = Label(_("Genre:"))
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.genreData)


	def genreData(self):
		#self.filmliste.append(("Neueste", "http://www.arte.tv/papi/tvguide/videos/plus7/program/D/L2/ALL/ALL/-1/AIRDATE_DESC/0/0/DE_FR.json"))
		#self.filmliste.append(("Meistgesehen", "http://www.arte.tv/papi/tvguide/videos/plus7/program/D/L2/ALL/ALL/-1/VIEWS/0/0/DE_FR.json"))
		#self.filmliste.append(("Letzte Chance", "http://www.arte.tv/papi/tvguide/videos/plus7/program/D/L2/ALL/ALL/-1/LAST_CHANCE/0/0/DE_FR.json"))
		#self.filmliste.append(("Themen", "by_channel"))
		self.filmliste.append(("Datum", "by_date"))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if 'http://' in Link:
			self.session.open(arteSecondScreen, Link, Name)
		else:
			self.session.open(arteSubGenreScreen, Link, Name)

class arteSubGenreScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("arte Mediathek")
		self['ContentTitle'] = Label(_("Genre:") + " %s" % Name)
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if self.Name == "Datum":
			today = datetime.date.today()
			for daynr in range(-21,22):
				day1 = today -datetime.timedelta(days=daynr)
				dateselect =  day1.strftime('%Y-%m-%d')
				link = 'https://www.arte.tv/guide/api/api/pages/de/web/TV_GUIDE/?day=%s' % dateselect
				self.filmliste.append((dateselect, link))
		elif self.Name == "Themen":
			link = 'http://www.arte.tv/papi/tvguide/videos/plus7/program/D/L2/%s/ALL/-1/AIRDATE_DESC/0/0/DE_FR.json'
			self.filmliste.append(('Aktuelles & Gesellschaft', link % 'ACT'))
			self.filmliste.append(('Fernsehfilme & Serien', link % 'FIC'))
			self.filmliste.append(('Kino', link % 'CIN'))
			self.filmliste.append(('Kunst & Kultur', link % 'ART'))
			self.filmliste.append(('Popkultur & Alternativ', link % 'CUL'))
			self.filmliste.append(('Entdeckung', link % 'DEC'))
			self.filmliste.append(('Geschichte', link % 'HIS'))
			self.filmliste.append(('Junior', link % 'JUN'))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.ml.moveToIndex(21)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(arteSecondScreen, Link, Name)

class arteSecondScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("arte Mediathek")
		self['ContentTitle'] = Label(_("Selection:") + " %s" % self.Name)

		self.page = 1
		self.lastpage = 1
		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		url = self.Link
		getPage(url, agent=std_headers, headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Referer': self.Link}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		json_data = json.loads(data)
		if json_data.has_key('zones'):
			for node in json_data["zones"][1]["data"]:
				if node['subtitle']:
					title = "%s - %s" % (str(node['title']), str(node['subtitle']))
				else:
					title = str(node['title'])
				m, s = divmod(node['duration'], 60)
				Runtime = _("Runtime:") + " %02d:%02d" % (m, s)				
				handlung = "%s\n%s" % (Runtime, str(node['fullDescription']))
				url = "https://api.arte.tv/api/player/v1/config/de/%s" % str(node['programId'])
				self.filmliste.append((title, url, str(node['images']['landscape']['resolutions'][-1]['url']), handlung))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No videos found!"), '','','','',''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self.ImageUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(_(title))
		self['handlung'].setText(handlung)
		CoverHelper(self['coverArt']).getCover(self.ImageUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		self.title = self['liste'].getCurrent()[0][0]
		link = self['liste'].getCurrent()[0][1]
		print link
		getPage(link, headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		json_data  = json.loads(data)
		if json_data["videoJsonPlayer"].has_key('VSR'):
			try:
				url = str(json_data["videoJsonPlayer"]["VSR"]["HTTPS_SQ_1"]["url"])
			except:
				url = None
		else:
			url = None
		if url:
			print url
			self.session.open(SimplePlayer, [(self.title, url, self.ImageUrl)], showPlaylist=False, ltype='arte')
		else:
			self.session.open(MessageBoxExt, _("This video is not available."), MessageBoxExt.TYPE_INFO, timeout=5)