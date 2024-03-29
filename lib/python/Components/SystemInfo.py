from os import path, listdir

from enigma import eDVBResourceManager, Misc_Options

from Tools.Directories import fileExists, fileCheck, fileHas, pathExists
from Tools.HardwareInfo import HardwareInfo

from boxbranding import getBoxType, getMachineBuild, getMachineProcModel, getBrandOEM, getDisplayType, getHaveRCA, getHaveDVI, getHaveYUV, getHaveSCART, getHaveAVJACK, getHaveSCARTYUV, getHaveHDMI, getMachineMtdKernel, getMachineMtdRoot

SystemInfo = { }

#FIXMEE...
def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d"% idx, 'f'):
		idx += 1
	return idx

SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["PIPAvailable"] = SystemInfo["NumVideoDecoders"] > 1
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds

SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["7segment"] = getBoxType() in ('sf8008','clap4k', 'dinobot4k', 'anadol4k', 'dinobot4kl', 'mediabox4k', 'dinobot4kse', 'dinobot4kplus', 'dinobot4kmini', 'axashis4kcombo', 'axashis4kcomboplus', 'osmini', 'osnino', 'osninoplus', 'osninopro', 'atemio6000', 'atemio6100', 'bwidowx', 'xpeedlx1', 'mutant1100', 'mutant1200', 'mutant1265', 'mutant1500', 'mutant500c', 'mutant530c', 'h3', 'h4', 'h5', 'h6', 'h7', 'formuler3', 'formuler3ip', 'formuler4', 'formuler4ip', 'formuler4turbo', 'spycatmini', 'spycatminiplus', 'xp1000', '9900lx', 'ew7358', 'ew7362', '7220s', '7300s', 'sh1', 'inihde2', 'inihde', 'odinm7', 'jj7362', 'vg2000', 'vg5000', 'vs1000', 'tiviarmin', 'g100', 'g101', 'xc7362', 'et1x000', 'xc7358')
SystemInfo["textlcd"] = getBoxType() in ('tiviaraplus','formuler1tc','zgemmah7','vimastec1000', 'vimastec1500','et7000', 'et7500', 'et8000', 'triplex', 'formuler1', 'mutant1200', 'solo2', 'osminiplus', 'ax51', 'mutant51', '9910lx', '9911lx')
SystemInfo["display96"] = getMachineBuild() in ('dm800sev2', 'dm800se', 'dm820')
SystemInfo["display128"] = getMachineBuild() in ('et10000')
SystemInfo["display140"] = getBoxType() in ('vuduo2')
SystemInfo["display220"] = getMachineBuild() in ('7100s', '7210s', '7105s', '7215s', '8100s') or getBoxType() in ('gb800ue', 'gbquad', 'gbultraue', 'gbultraueh', 'gbue4k', 'gb800ueplus', 'e4hdultra')
SystemInfo["display255"] = getMachineBuild() in ('hd2400', 'inihdp', 'vuultimo')
SystemInfo["display390"] = getBoxType() in ('dm900')
SystemInfo["display400"] = getBoxType() in ('gbquadplus', 'gbquad4k', 'dm920', 'vuuno4kse')
SystemInfo["display480"] = getBoxType() in ('vusolo4k')
SystemInfo["display720"] = getBoxType() in ('et8500')
SystemInfo["display800"] = getBoxType() in ('vuultimo4k')
SystemInfo["ConfigDisplay"] = SystemInfo["FrontpanelDisplay"] and not SystemInfo["7segment"]
SystemInfo["LCDSKINSetup"] = path.exists("/usr/share/enigma2/display") and not SystemInfo["7segment"]
SystemInfo["12V_Output"] = Misc_Options.getInstance().detected_12V_output()
SystemInfo["ZapMode"] = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["OledDisplay"] = fileExists("/dev/dbox/oled0") or getBoxType() in ('osminiplus')
SystemInfo["LcdDisplay"] = fileExists("/dev/dbox/lcd0")
SystemInfo["FBLCDDisplay"] = fileCheck("/proc/stb/fb/sd_detach")
SystemInfo["VfdDisplay"] = getBoxType() not in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'atemionemesis') and fileExists("/dev/dbox/oled0")
SystemInfo["DeepstandbySupport"] = HardwareInfo().has_deepstandby()
SystemInfo["Fan"] = fileCheck("/proc/stb/fp/fan")
SystemInfo["FanPWM"] = SystemInfo["Fan"] and fileCheck("/proc/stb/fp/fan_pwm")
SystemInfo["StandbyPowerLed"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["LEDButtons"] = getBoxType() == 'vuultimo'
SystemInfo["WakeOnLAN"] = fileCheck("/proc/stb/power/wol") or fileCheck("/proc/stb/fp/wol")
if getBoxType() in ('gbquad', 'gbquadplus','gb800ueplus', 'gb800seplus', 'gbipbox'):
	SystemInfo["WOL"] = False
else:
	SystemInfo["WOL"] = fileCheck("/proc/stb/power/wol") or fileCheck("/proc/stb/fp/wol")
SystemInfo["HDMICEC"] = (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo")
SystemInfo["SABSetup"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/SABnzbd/plugin.pyo")
SystemInfo["SeekStatePlay"] = False
SystemInfo["GraphicLCD"] = getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4')
SystemInfo["Blindscan"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Blindscan/plugin.pyo")
SystemInfo["Satfinder"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Satfinder/plugin.pyo")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["GBWOL"] = fileExists("/usr/bin/gigablue_wol")
SystemInfo["VFD_scroll_repeats"] = fileCheck("/proc/stb/lcd/scroll_repeats")
SystemInfo["VFD_scroll_delay"] = fileCheck("/proc/stb/lcd/scroll_delay")
SystemInfo["VFD_initial_scroll_delay"] = fileCheck("/proc/stb/lcd/initial_scroll_delay")
SystemInfo["VFD_final_scroll_delay"] = fileCheck("/proc/stb/lcd/final_scroll_delay")
SystemInfo["LCDMiniTV"] = fileExists("/proc/stb/lcd/mode")
SystemInfo["LCDMiniTVPiP"] = SystemInfo["LCDMiniTV"] and getBoxType() != 'gb800ueplus'
SystemInfo["LcdLiveTV"] = fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable")
SystemInfo["LcdLiveTVPiP"] = fileCheck("/proc/stb/lcd/live_decoder")
SystemInfo["LCDMiniTV4k"] = fileExists("/proc/stb/lcd/live_enable")
SystemInfo["isGBIPBOX"] = fileExists("/usr/lib/enigma2/python/gbipbox.so")
SystemInfo["MiniTV"] = fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable")
SystemInfo["FastChannelChange"] = False
SystemInfo["CIHelper"] = fileExists("/usr/bin/cihelper")
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
SystemInfo["CanUse3DModeChoices"] = fileExists('/proc/stb/fb/3dmode_choices') and True or False
SystemInfo["need_dsw"] = getBoxType() not in ('osminiplus','osmega')
SystemInfo["HaveCISSL"] = fileCheck("/etc/ssl/certs/customer.pem") and fileCheck("/etc/ssl/certs/device.pem")
SystemInfo["HaveID"] = fileCheck("/etc/.id")
SystemInfo["HaveTouchSensor"] = getBoxType() in ('dm520', 'dm525', 'dm900', 'dm920')
SystemInfo["DefaultDisplayBrightness"] = getBoxType() in ('dm900', 'dm920') and 8 or 5
SystemInfo["canMultiBoot"] = getMachineBuild() in ('hd51','vs1500','h7','h9combo','hd60','hd61','multibox','8100s') and (1, 4, 'mmcblk0p') or getMachineBuild() in ('gb7252') and (3, 3, 'mmcblk0p') or getMachineBuild() in ('gbmv200','cc1','sf8008','ustym4kpro','beyonwizv2','viper4k') and fileCheck("/dev/sda") and (0, 3, 'sda') or getMachineBuild() in ('osmio4k','osmio4kplus','xc7439') and (1, 4, 'mmcblk1p')
SystemInfo["HAScmdline"] = fileCheck("/boot/cmdline.txt")
SystemInfo["HasMMC"] = fileHas("/proc/cmdline", "root=/dev/mmcblk") or SystemInfo["canMultiBoot"] and fileHas("/proc/cmdline", "root=/dev/sda")
SystemInfo["HasSDmmc"] = SystemInfo["canMultiBoot"] and "sd" in SystemInfo["canMultiBoot"][2] and "mmcblk" in getMachineMtdRoot() 
SystemInfo["HasSDswap"] = getMachineBuild() in ("h9", "i55plus") and pathExists("/dev/mmcblk0p1")
SystemInfo["CanProc"] = SystemInfo["HasMMC"] and getBrandOEM() != "vuplus"
SystemInfo["canRecovery"] = getMachineBuild() in ('hd51','vs1500','h7','8100s') and ('disk.img', 'mmcblk0p1') or getMachineBuild() in ('xc7439','osmio4k','osmio4kplus') and ('emmc.img', 'mmcblk1p1') or getMachineBuild() in ('gbmv200','cc1','sf8008','ustym4kpro','beyonwizv2','viper4k') and ('usb_update.bin','none')
SystemInfo["canMode12"] = getMachineBuild() in ('hd51','vs1500','h7') and ('brcm_cma=440M@328M brcm_cma=192M@768M', 'brcm_cma=520M@248M brcm_cma=200M@768M')
SystemInfo["HasRootSubdir"] = fileHas("/proc/cmdline", "rootsubdir=")
SystemInfo["RecoveryMode"] = SystemInfo["HasRootSubdir"] and getMachineBuild() not in ('vs1500','hd51','h7') or fileCheck("/proc/stb/fp/boot_mode")
SystemInfo["ForceLNBPowerChanged"] = fileCheck("/proc/stb/frontend/fbc/force_lnbon")
SystemInfo["ForceToneBurstChanged"] = fileCheck("/proc/stb/frontend/fbc/force_toneburst")
SystemInfo["USETunersetup"] = SystemInfo["ForceLNBPowerChanged"] or SystemInfo["ForceToneBurstChanged"]
SystemInfo["XcoreVFD"] = getMachineBuild() in ('xc7346','xc7439') 
SystemInfo["HDMIin"] = getMachineBuild() in ('inihdp', 'hd2400', 'et10000', 'dm7080', 'dm820', 'dm900', 'dm920', 'vuultimo4k', 'et13000', 'sf5008', 'vuuno4kse', 'vuduo4k') or getBoxType() in ('spycat4k','spycat4kcombo','gbquad4k')
