import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon('script.leuthil.netflixchecker')
addonname = addon.getAddonInfo('name')
icon = addon.getAddonInfo('icon')

package = '"%s"' % addon.getSetting('package')
intent = '"%s"' % addon.getSetting('intent')
datatype = '"%s"' % addon.getSetting('datatype')
uri = addon.getSetting('uri')
movieId = '18171022'
movieURL = '"'+uri.replace('{id}',movieId)+'"'

xbmc.executebuiltin('XBMC.StartAndroidActivity(%s,%s,%s,%s)' % (package, intent, datatype, movieURL))