# -*- coding: utf-8 -*-
from enigma import gFont, addFont, eTimer, eConsoleAppContainer, ePicLoad, loadPNG, getDesktop, eServiceReference, iPlayableService, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListbox, gPixmapPtr, getPrevAsciiCode, eBackgroundFileEraser

from Plugins.Plugin import PluginDescriptor

from twisted import __version__
from twisted.internet import reactor, defer
from twisted.web.http_headers import Headers
from twisted.internet.defer import Deferred, succeed
from twisted.web import http
from twisted.python import failure

from twisted.web import error as weberror

from cookielib import CookieJar

from zope.interface import implements

from twagenthelper import TwAgentHelper, twAgentGetPage
from tw_util import downloadPage, getPage
from sepg.mp_epg import SimpleEPG, mpepg, mutex
from sepg import log

from Components.ActionMap import NumberActionMap, ActionMap, HelpableActionMap
from Components.AVSwitch import AVSwitch
from Components.Button import Button
from Components.config import config, ConfigInteger, ConfigSelection, getConfigListEntry, ConfigText, ConfigDirectory, ConfigYesNo, configfile, ConfigSelection, ConfigSubsection, ConfigPIN, NoSave, ConfigNothing, ConfigIP
try:
	from Components.config import ConfigPassword
except ImportError:
	ConfigPassword = ConfigText
try:
	from Components.config import ConfigOnOff
except ImportError:
	from Components.config import ConfigEnableDisable
	ConfigOnOff = ConfigEnableDisable
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.Boolean import Boolean
from Components.Input import Input

from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarNotifications

from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.NumericalTextInputHelpDialog import NumericalTextInputHelpDialog
from Screens.HelpMenu import HelpableScreen

from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_FONTS, createDir
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput

import re, urllib, urllib2, os, cookielib, socket, sha, shutil, datetime, math, hashlib, random, json, md5, string, xml.etree.cElementTree, StringIO, Queue, threading, sys

from urllib2 import Request, URLError, urlopen as urlopen2
from socket import gaierror, error
from urllib import quote, unquote_plus, unquote, urlencode
from binascii import unhexlify, hexlify
from urlparse import parse_qs
from time import time, localtime, strftime, mktime

# MediaPortal Imports
from debuglog import printlog as printl

class InsensitiveKey(object):
	def __init__(self, key):
		self.key = key
	def __hash__(self):
		return hash(self.key.lower())
	def __eq__(self, other):
		return self.key.lower() == other.key.lower()
	def __str__(self):
		return self.key

class InsensitiveDict(dict):
	def __setitem__(self, key, value):
		key = InsensitiveKey(key)
		super(InsensitiveDict, self).__setitem__(key, value)
	def __getitem__(self, key):
		key = InsensitiveKey(key)
		return super(InsensitiveDict, self).__getitem__(key)

def r_getPage(url, *args, **kwargs):
	def retry(err):
		return getPage(url.replace('https:','http:'), *args, **kwargs)
	return twAgentGetPage(url, *args, **kwargs).addErrback(retry)

import mp_globals

#if mp_globals.isDreamOS:
#	from pixmapext import PixmapExt as Pixmap

try:
	from Screens.InfoBarGenerics import InfoBarServiceErrorPopupSupport
except:
	class InfoBarServiceErrorPopupSupport:
		def __init__(self):
			pass

try:
	from Screens.InfoBarGenerics import InfoBarGstreamerErrorPopupSupport
	mp_globals.stateinfo = True
except:
	class InfoBarGstreamerErrorPopupSupport:
		def __init__(self):
			mp_globals.stateinfo = False

from mp_globals import std_headers
from streams import isSupportedHoster, get_stream_link
from mpscreen import MPScreen, MPSetupScreen, SearchHelper
from simpleplayer import SimplePlayer
from coverhelper import CoverHelper
from showAsThumb import ThumbsHelper
from messageboxext import MessageBoxExt

def registerFont(file, name, scale, replacement):
	addFont(file, name, scale, replacement)

def getUserAgent():
	userAgents = [
		"Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
		"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52",
		"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20120101 Firefox/35.0",
		"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0",
		"Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
		"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
		"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
		"Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)",
		"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
	]
	return random.choice(userAgents)

def getUpdateUrl():
	updateurls = [
		'http://master.dl.sourceforge.net/project/e2-mediaportal/version.txt',
		'http://dhwz.github.io/e2-mediaportal/version.txt',
		'http://dhwz.gitlab.io/pages/version.txt'
	]
	return random.choice(updateurls)

def getIconUrl():
	iconurls = [
		'http://dhwz.gitlab.io/pages/',
		'http://dhwz.github.io/e2-mediaportal/',
		'http://dhwz.gitlab.io/pages/'
	]
	return random.choice(iconurls)

def bstkn(url):
	urlpart = re.search('https://bs.to/api/(.*?)$', url)
	if urlpart:
		import hmac, base64
		urlpart = urlpart.group(1)
		datelong = int(round(time()))
		public_key = base64.b64decode('UGdmTGEzY0dOWTVuRE4zaXNpYnp1R3NvbVNXc3BqQXM=')
		resultD = mp_globals.bsp
		myurlpart = '%s/%s' % (datelong, urlpart)
		myHmac = hmac.new(resultD, myurlpart,digestmod=hashlib.sha256).hexdigest()
		token = '{"public_key":"'+public_key+'","timestamp":'+str(datelong)+',"hmac":"'+ myHmac+'"}'
		retval = base64.b64encode(token)
		return retval
	else:
		return None

def testWebConnection():
	import requests
	try:
		response = requests.get("http://www.google.de", timeout=5)
		return True
	except requests.ConnectionError:
		return False

def decodeHtml(text):
	import HTMLParser
	h = HTMLParser.HTMLParser()
	text = h.unescape(text).encode('utf-8')
	text = h.unescape(text).encode('utf-8')
	text = text.decode('unicode-escape').decode('utf-8').encode('latin1')
	return text

def stripAllTags(html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr,'', html.replace('\n',''))
	return cleantext