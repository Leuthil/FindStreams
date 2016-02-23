import sys
import xbmc
import xbmcaddon
import xbmcgui
import urllib2
import json

# Initialization
findstreams = xbmcaddon.Addon('context.findstreams.contextmenu')
# Hard-coded list of all regions with their enum id
fullRegionList = {
    '0': 'en_AU', #Australia
    '1': 'pt_BR', #Brazil
    '2': 'en_CA', #Canada
    '3': 'de_DE', #Germany
    '4': 'en_IE', #Ireland
    '5': 'en_NZ', #New Zealand
    '6': 'en_ZA', #South Africa
    '7': 'en_GB', #United Kingdom
    '8': 'en_US'  #United States
}
# Hard-coded list of all providers
fullProviderList = [
    'netflix',
    'crackle',
    'itunes',
    'play',
    'playstation',
    'xbox',
    'fandor',
    'mubi',
    'amazonprime',
    'hbonow',
    'huluplus',
    'hulu',
    'epix',
    'showtime',
    'starz',
    'amazon',
    'vudu',
    'realeyz',
    'shomi',
    'cravetv'
]
# Hard-coded list of all monetization types
fullMonetizationList = [
    'flatrate',
    'free',
    'ads',
    'buy',
    'rent',
    'cinema'
]
# Hard-coded list of all presentation types
fullPresentationList = [
    'hd',
    'sd'
]

###
# Get offers for a movie/show title
# params
#   search_query - string Movie/show title - format 'Title (Year)' for highest accuracy
#   content_type - list List containing whether to search for title as a show, movie or both (ex. ['show', 'movie'])
# return - dict Stream info and stream offerings
#   dict['title']                   Movie/Show Title
#   dict['year']                    Movie/Show Release Year
#   dict['object_type']             Object Type - movie, show
#   dict['provider_id']             JustWatch.com Internal Provider ID (not really necessary but why not)
#   dict['provider_name']           Provider Name
#   dict['monetization_type']       Monetization Type - flatrate, ads, free, buy, rent, cinema
#   dict['presentation_type']       Presentation Type - hd, sd
#   dict['retail_price']            Retail price (Returns as 0 if it was null)
#   dict['currency']                Currency (empty string if retail price was null)
#   dict['element_count']           Number of Seasons available (may be 0 if a movie... not sure)
#   dict['offers']                  List of offers
###
def getStreamOffers(search_query, content_type):
    ## user addon settings ##
    region = getRegionFilter()
    monetization_type_filter = getMonetizationFilter()
    presentation_type_filter = getPresentationFilter()
    provider_filter = getProviderFilter()
    providers = getProviders(region)

    # monetization type filter is empty then use all
    if len(monetization_type_filter) == 0:
        monetization_type_filter = fullMonetizationList
    # presentation type filter is empty then use all
    if len(presentation_type_filter) == 0:
        presentation_type_filter = fullPresentationList
    # provider filter is empty then use all from region
    if len(provider_filter) == 0:
        for prov in providers:
            provider_filter.append(providers[prov]['technical_name'])

    # we only ever care about first result... should be good enough and helps limit bandwidth
    data = {
            "query": search_query,
            "content_types": content_type,
            "page":1,
            "page_size":1
            }
    jsonData = json.dumps(data)
    url = "https://api.justwatch.com/titles/%s/popular" % region
    headers = {
               'Host': 'api.justwatch.com',
               'Connection': 'keep-alive',
               'Origin': 'https://www.justwatch.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
               'Content-Type': 'application/json;charset=UTF-8',
               }
    req = urllib2.Request(url, jsonData, headers)
    resp = urllib2.urlopen(req)
    html = resp.read()
    json_dict = json.loads(html)
    result = '%s (%s) is available on:' % (json_dict['items'][0]['title'], json_dict['items'][0]['original_release_year'])
    
    #filter offers based on user addon settings
    filtered_offers = []
    for value in json_dict['items'][0]['offers']:
        if 'retail_price' not in value:
            value['retail_price'] = 0
            value['currency'] = ''
        if value['presentation_type'] in presentation_type_filter and value['monetization_type'] in monetization_type_filter and providers[value['provider_id']]['technical_name'] in provider_filter:
            filtered_offers.append(value)
    
    # sort based on price... for now
    result = {}
    result['title'] = json_dict['items'][0]['title']
    result['year'] = json_dict['items'][0]['original_release_year']
    result['object_type'] = json_dict['items'][0]['object_type']
    result['offers'] = []
    for value in sorted(filtered_offers, key=lambda off: off['retail_price']):
        offer = {}
        offer['provider_id'] = value['provider_id']
        offer['provider_name'] = providers[value['provider_id']]['clear_name']
        offer['provider_technicalname'] = providers[value['provider_id']]['technical_name']
        offer['monetization_type'] = value['monetization_type']
        offer['presentation_type'] = value['presentation_type']
        offer['retail_price'] = value['retail_price']
        offer['url'] = ''
        if offer['retail_price'] > 0:
            offer['currency'] = value['currency']
        if 'element_count' in value and 'show' in result['object_type']:
            offer['element_count'] = value['element_count']
        if 'urls' in value and 'standard_web' in value['urls']:
            offer['url'] = value['urls']['standard_web']
        result['offers'].append(offer)
    return result

###
# Get stream providers for a specified region
# params
#   region - string Region to get providers from
# return - dict Dictionary of providers where key is provider_id
###
def getProviders(region):
    url = "https://api.justwatch.com/providers/locale/%s" % region
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    html = resp.read()
    json_dict = json.loads(html)
    providers = {}
    for provider in json_dict:
        providers[provider['id']] = provider
    return providers

###
# Returns list of filtered provided based on user settings
# return - list Desired providers
###
def getRegionFilter():
    region = ''
    regionSetting = findstreams.getSetting('region')
    if regionSetting in fullRegionList:
        region = fullRegionList[regionSetting]
    return region

###
# Returns list of monetization types to filter by based on user settings
# return - list Desired monetization types
###
def getMonetizationFilter():
    monetization_types = []
    for monetization in fullMonetizationList:
        if findstreams.getSetting('monetization_%s' % monetization) == 'true':
            monetization_types.append(monetization)
    return monetization_types

###
# Returns list of presentation types to filter by based on user settings
# return - list Desired presentation types
###
def getPresentationFilter():
    presentation_types = []
    for presentation in fullPresentationList:
        if findstreams.getSetting('presentation_%s' % presentation) == 'true':
            presentation_types.append(presentation)
    return presentation_types

###
# Returns list of providers to filter by based on user settings
# return - list Desired providers
###
def getProviderFilter():
    providers = []
    for prov in fullProviderList:
        if findstreams.getSetting('provider_%s' % prov) == 'true':
            providers.append(prov)
    return providers

###
# DescriptionOfWhatThisDoes
# params
#   firstParam - type WhatParamIs
# return - type WhatReturnIs
###
def stub():
    test = ''

### CORE LOGIC ###
if __name__ == '__main__':
    title = xbmc.getInfoLabel('ListItem.Title')
    content_type = xbmc.getInfoLabel('ListItem.DBTYPE')
    content = []
    totalSeasons = 0
    if content_type in ['tvshow', 'season', 'episode']:
        title = xbmc.getInfoLabel('ListItem.TVShowTitle')
        totalSeasons = xbmc.getInfoLabel('ListItem.Property(TotalSeasons)')
        content.append('show')
    else:
        content.append('movie')
    year = xbmc.getInfoLabel('ListItem.Year')
    titleYear = "%s (%s)" % (title, year)
    if getRegionFilter() == '':
        findstreams.openSettings()
        xbmcgui.Dialog().notification('Setup', 'Please choose a region!')
    else:
        streamResults = getStreamOffers(titleYear, content)
        if len(streamResults) < 1 or 'offers' not in streamResults or len(streamResults['offers']) < 1 or (streamResults['year'] != year and streamResults['title'] != title):
            xbmcgui.Dialog().notification('%s Streams' % titleYear, 'No streams found!')
        else:
            offerStrings = []
            for offer in streamResults['offers']:
                offerString = '%s on %s in %s' % (offer['monetization_type'].title(), offer['provider_name'], offer['presentation_type'].upper())
                if offer['retail_price'] > 0:
                    offerString += ' for $%s %s' % (round(offer['retail_price'], 2), offer['currency'])
                if 'element_count' in offer and streamResults['object_type'] == 'show':
                    offerString += ' - %s/%s Seasons' % (offer['element_count'], totalSeasons)
                offerStrings.append(offerString)
            selection = xbmcgui.Dialog().select('%s (%s) Streams' % (streamResults['title'], streamResults['year']), offerStrings)
            xbmcgui.Dialog().notification('Stream Selected', 'Selected from provider %s' % streamResults['offers'][selection]['provider_technicalname'])
            #if streamResults['offers'][selection]['provider_technicalname'] == 'play':
            xbmc.executebuiltin('XBMC.StartAndroidActivity(%s,%s,%s,"%s")' % (findstreams.getSetting('action_play_package'), findstreams.getSetting('action_play_intent'), findstreams.getSetting('action_play_datatype'), streamResults['offers'][selection]['url']))
