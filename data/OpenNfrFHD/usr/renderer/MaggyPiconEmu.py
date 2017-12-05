from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from Renderer import Renderer
from enigma import ePixmap, eTimer
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.config import config
from Components.Converter.Poll import Poll

class MaggyPiconEmu(Renderer, Poll):
    __module__ = __name__
    searchPaths = ('/usr/share/enigma2/%s/', '/media/hdd/%s/', '/media/usb/%s/', '/media/sda1/%s/')

    def __init__(self):
        Poll.__init__(self)
        Renderer.__init__(self)
        self.path = 'emu'
        self.nameCache = {}
        self.pngname = ''

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        self.poll_interval = 2000
        self.poll_enabled = True
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                text = 'none'
                if fileExists('/etc/CurrentBhCamName'):
                    f = open('/etc/CurrentBhCamName', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
                elif fileExists('/var/etc/client'):
                    f = open('/var/etc/client', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
                elif fileExists('/tmp/.emu.info'):
                    f = open('/tmp/.emu.info', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
                elif fileExists('/etc/active_emu.list'):
                    f = open('/etc/active_emu.list', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
                elif fileExists('/tmp/egami.inf'):
                    f = open('/tmp/egami.inf', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
                elif fileExists('/etc/init.d/softcam'):
                    f = open('/etc/init.d/softcam', 'r')
                    line = f.readline()
                    text = line.strip()
                    f.close()
		elif config.NFRSoftcam.actcam.value:
			if config.NFRSoftcam.actcam.value != "none":
				camdlist = config.NFRSoftcam.actcam.value.split()
			else: 
                        	camdlist = 'none'	
			for line in camdlist:
				if 'mgcamd' in line.lower() and 'oscam' in line.lower():
					text = 'oscammgcamd'
					break
				if 'cccam' in line.lower() and 'oscam' in line.lower():
					text = 'oscamcccam'
					break
				elif 'mgcamd' in line.lower():
					text = 'mgcamd'
				elif 'oscam' in line.lower():
					text = 'oscam'
				elif 'wicard' in line.lower():
					text = 'wicardd'
				elif 'cccam' in line.lower():
					text = 'cccam'
				elif 'camd3' in line.lower():
					text = 'camd3'
				elif 'evocamd' in line.lower():
					text = 'evocamd'
				elif 'newcs' in line.lower():
					text = 'newcs'
				elif 'rqcamd' in line.lower():
					text = 'rqcamd'
				elif 'gbox' in line.lower():
					text = 'gbox'
				elif 'mpcs' in line.lower():
					text = 'mpcs'
				elif 'sbox' in line.lower():
					text = 'sbox'
                                else:
					text = 'unknow'                                                                          
                pngname = self.nameCache.get(text, '')
                if pngname == '':
                    pngname = self.findEmu(text)
                    if pngname != '':
                        self.nameCache[text] = pngname
            if pngname == '':
                pngname = self.nameCache.get('no_cam', '')
                if pngname == '':
                    pngname = self.findEmu('picon_no_cam')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_no_cam.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                    self.nameCache['default'] = pngname
            if self.pngname != pngname:
                self.pngname = pngname
                self.instance.setPixmapFromFile(self.pngname)

    def findEmu(self, serviceName):
        for path in self.searchPaths:
            pngname = path % self.path + serviceName + '.png'
            if fileExists(pngname):
                return pngname

        return ''