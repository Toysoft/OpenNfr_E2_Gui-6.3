# -*- coding: utf-8 -*-
import datetime
import os
import sys
from config import config_mp

mp_LogFile = None

# ****************************** VERBOSITY Level *******************************
VERB_ERROR       = 1  # "E" shows error
VERB_WARNING     = 2  # "W" shows warning
VERB_STARTING    = 3  # "S" shows started functions/classes etc.
VERB_HIGHLIGHT   = 4  # "H" shows important hightlights to have better overview if somehtings really happening or not
VERB_ADDITIONAL  = 5  # "A" shows additional information for better debugging
VERB_CLOSING     = 6  # "C" shows closing functions/classes etc.
VERB_DEFAULT     = 10 # "I" default verbose level when not specified
VERB_TOLOG       = 20 # " " max verbose level that shows up in normal log

def printl(string, parent=None, verbLevel=VERB_DEFAULT):
	debugMode = config_mp.mediaportal.debugMode.value
	type = "I"
	if verbLevel == "E":
		verbLevel = 1
		type = "E"
	elif verbLevel == "W":
		verbLevel = 2
		type = "W"
	elif verbLevel == "S":
		verbLevel = 3
		type = "S"
	elif verbLevel == "H":
		verbLevel = 4
		type = "H"
	elif verbLevel == "A":
		verbLevel = 5
		type = "A"
	elif verbLevel == "C":
		verbLevel = 6
		type = "C"
	elif verbLevel == "I":
		verbLevel = 10
		type = "I"
	out = ""
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			out = str(classname) + str(sys._getframe(1).f_code.co_name) +" " + str(string)
		else:
			classname = ""
			out = str(parent) + str(string)
	if verbLevel == VERB_ERROR:
		print '\033[1;41m' + "[MediaPortal] " + "E" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	elif verbLevel == VERB_WARNING:
		print '\033[1;33m' + "[MediaPortal] " + "W" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	elif verbLevel == VERB_STARTING and debugMode == "High":
		print '\033[0;36m' + "[MediaPortal] " + '\033[1;m' + '\033[1;32m' + "S" + "  " + str(out) + '\033[1;m'
		if debugMode != "Silent":
			writeToLog(type, out)
	elif verbLevel == VERB_HIGHLIGHT and debugMode == "High":
		print '\033[0;36m' + "[MediaPortal] " + '\033[1;m' + '\033[1;37m' + "H" + "  " + str(out) + '\033[1;m'
		if debugMode != "Silent":
			writeToLog(type, out)
	elif verbLevel == VERB_ADDITIONAL and debugMode == "High":
		print '\033[0;36m' + "[MediaPortal] " + '\033[1;m' + '\033[1;32m' + "A" + "  " + str(out) + '\033[1;m'
		if debugMode != "Silent":
			writeToLog(type, out)
	elif verbLevel == VERB_CLOSING and debugMode == "High":
		print '\033[0;36m' + "[MediaPortal] " + '\033[1;m' + '\033[1;32m' + "C" + "  " + str(out) + '\033[1;m'
		if debugMode != "Silent":
			writeToLog(type, out)
	elif verbLevel <= VERB_TOLOG:
		print '\033[0;36m' + "[MediaPortal] " + "I" + "  " + '\033[1;m' + str(out)
		if debugMode != "Silent":
			writeToLog(type, out)
	elif verbLevel > VERB_TOLOG:
		print '\033[0;36m' + "[MediaPortal] " + "only onScreen" + "  " + str(out) + '\033[1;m'

def writeToLog(type, out):
	global mp_LogFile
	if mp_LogFile is None:
		openLogFile()
	now = datetime.datetime.now()
	mp_LogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + str(type) + "  " + str(out) + "\n")
	mp_LogFile.flush()

def openLogFile():
	global mp_LogFile
	baseDir = "/tmp"
	logDir = baseDir + "/mediaportal"
	now = datetime.datetime.now()
	try:
		os.makedirs(baseDir)
	except OSError, e:
		pass
	try:
		os.makedirs(logDir)
	except OSError, e:
		pass
	mp_LogFile = open(logDir + "/MediaPortal_%04d%02d%02d_%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")