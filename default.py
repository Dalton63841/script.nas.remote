import xbmc
import xbmcgui
import xbmcaddon
import os
import struct
import socket
import sys
import commands

__addon__ = xbmcaddon.Addon()
icon = __addon__.getAddonInfo('icon')
ipadd = __addon__.getSetting("ipaddress")
mac = __addon__.getSetting("macaddress")
user = __addon__.getSetting("username")
command = __addon__.getSetting("command")
port = __addon__.getSetting("port")

dialog = xbmcgui.Dialog()
entries = ["Power On/Off", "Send A Command"]
nr = dialog.select("What Would You Like To Do?", entries)
if nr == 0:
    xbmc.executebuiltin('Notification(Nas Remote,Checking Remote Server Status,5000,%s)' % icon)
    result = commands.getoutput("ping -c1 " + ipadd)
    if result.find("100% packet loss") == -1:
        xbmc.executebuiltin('Notification(Nas Remote,Shutting Down Remote Server,3000,%s)' % icon)
        os.system('ssh -p %s %s@%s %s ' % (port, user, ipadd, command))
        result = True
        while (result == True):
            check = commands.getoutput("ping -c1 " + ipadd)
            if check.find("100% packet loss") != -1:
                result = False
                xbmc.executebuiltin('Notification(Nas Remote,Server has successfully powered off,3000,%s)' % icon)
    else:
        xbmc.executebuiltin('Notification(Nas Remote,Waking Remote Server,3000,%s)' % icon)
        xbmc.executebuiltin("WakeOnLan(%s)" % mac)
        result = False
        while (result == False):
            check = commands.getoutput("ping -c1 " + ipadd)
            if check.find("100% packet loss") == -1:
                result = True
                xbmc.executebuiltin('Notification(Nas Remote,Server has successfully powered on,3000,%s)' % icon)
elif nr==1:
    dialog = xbmcgui.Dialog()
    cmd_input = dialog.input('Enter Command', type=xbmcgui.INPUT_ALPHANUM)
    if cmd_input != '':
        xbmc.executebuiltin('Notification(Nas Remote,Sending Command,3000,%s)' % icon)
        cmd_path = xbmc.translatePath("special://masterprofile/addon_data/script.nas.remote")
        os.system('ssh -p %s -o loglevel=error %s@%s %s &> %s/cmd.txt' % (port, user, ipadd, cmd_input, cmd_path)) 
        output = commands.getoutput("cat %s/cmd.txt" % cmd_path)
        if output != '':
            class Viewer:
                # constants
                WINDOW = 10147
                CONTROL_LABEL = 1
                CONTROL_TEXTBOX = 5

                def __init__( self, *args, **kwargs ):
                    # activate the text viewer window
                    xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
                    # get window
                    self.window = xbmcgui.Window( self.WINDOW )
                    # give window time to initialize
                    xbmc.sleep( 100 )
                    # set controls
                    self.setControls()

                def setControls( self ):
                    #get header, text
                    heading, text = self.getText()
                    # set heading
                    self.window.getControl( self.CONTROL_LABEL ).setLabel( "Command Output" )
                    # set text
                    self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

                def getText( self ):
                    try:
                        txt = open( os.path.join("%s/cmd.txt" % cmd_path) ).read()
                        return "cmd", txt
                    except:
                        print_exc()
                    return "", ""

            Viewer()
        else:
             xbmc.executebuiltin('Notification(Nas Remote,No Output to Report,3000,%s)' % icon)

