# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.additions.mediatheken.tvnow import tvnowFirstScreen, tvnowSubGenreScreen, tvnowStaffelScreen, tvnowEpisodenScreen

default_cover = "file://%s/tvnow.png" % (config.mediaportal.iconcachepath.value + "logos")

class tvnowGZFirstScreen(tvnowFirstScreen):

	def __init__(self, session):
		tvnowFirstScreen.__init__(self, session)

	def genreData(self):
		self.senderliste.append(("RTL", "rtl", default_cover))
		self.senderliste.append(("VOX", "vox", default_cover))
		self.senderliste.append(("RTL2", "rtl2", default_cover))
		self.senderliste.append(("NITRO", "nitro",  default_cover))
		self.senderliste.append(("SUPER RTL", "superrtl", default_cover))
		self.senderliste.append(("RTLplus", "rtlplus",  default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.senderliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.senderliste, 0, 1, 2, None, None, 1, 1, mode=1)
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Image = self['liste'].getCurrent()[0][2]
		self.session.open(tvnowGZSubGenreScreen, Link, Name, Image)

class tvnowGZSubGenreScreen(tvnowSubGenreScreen):

	def __init__(self, session, Link, Name, Image):
		tvnowSubGenreScreen.__init__(self, session, Link, Name, Image)

	def parseData(self, data):
		nowdata = json.loads(data)
		for node in nowdata["items"]:
			image = str(node["defaultImage169Logo"])
			if image == "":
				image = str(node["defaultImage169Format"])
			if image == "":
				image = self.Image
			self.filmliste.append((str(node["title"]), str(node["seoUrl"]), image))
		self.filmliste.sort(key=lambda t : t[0].lower())
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, 1, 1, mode=1)
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self.Name + ":" + self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Image = self['liste'].getCurrent()[0][2]
		self.session.open(tvnowGZStaffelScreen, Link, Name, Image)

class tvnowGZStaffelScreen(tvnowStaffelScreen):

	def __init__(self, session, Link, Name, Image):
		tvnowStaffelScreen.__init__(self, session, Link, Name, Image)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self.Name + ":" + self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			self.session.open(tvnowGZEpisodenScreen, Link, Name, self.Image)

class tvnowGZEpisodenScreen(tvnowEpisodenScreen):

	def __init__(self, session, Link, Name, Image):
		tvnowEpisodenScreen.__init__(self, session, Link, Name, Image)

	def parseData(self, data):
		nowdata = json.loads(data)
		try:
			for node in nowdata["formatTabPages"]["items"]:
				try:
					try:
						containerid = str(node["container"]["id"])
						if containerid:
							self.container += 1
							self.loadContainer(containerid)
					except:
						for nodex in node["container"]["movies"]["items"]:
							try:
								if not nodex["isDrm"]:
									try:
										image = "http://ais.tvnow.de/rtlnow/%s/660x660/formatimage.jpg" % nodex["pictures"]["default"][0]["id"]
									except:
										image = self.Image
									descr = str(nodex["articleLong"])
									if descr == "":
										descr = str(nodex["articleShort"])
									self.filmliste.append((str(nodex["title"]), str(nodex["id"]), descr, image))
							except:
								continue
				except:
					continue
			self.parseContainer("", False)
		except:
			pass

	def parseContainer(self, data, id=False):
		if id:
			self.container -= 1
			nowdata = json.loads(data)
			try:
				for nodex in nowdata["items"]:
					try:
						if not nodex["isDrm"]:
							try:
								image = "http://ais.tvnow.de/rtlnow/%s/660x660/formatimage.jpg" % nodex["pictures"]["default"][0]["id"]
							except:
								image = self.Image
							descr = str(nodex["articleLong"])
							if descr == "":
								descr = str(nodex["articleShort"])
							self.filmliste.append((str(nodex["title"]), str(nodex["id"]), descr, image))
					except:
						continue
			except:
				pass
		if self.container == 0:
			if len(self.filmliste) == 0:
				self.filmliste.append((_('Currently no free episodes available!'), None, None, None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.keyLocked = False
			self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, 1, 1, mode=1)
			self.showInfos()