import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
icon = addon.getAddonInfo('icon')

intent = '"android.intent.action.VIEW"'
netflixURL = 'https://www.netflix.com/watch/'
movieId = '18171022'
movieURL = '"'+netflixURL+movieId+'"'

xbmc.executebuiltin('StartAndroidActivity(%s,%s,%s,%s)' % ("", intent, "", movieURL))
