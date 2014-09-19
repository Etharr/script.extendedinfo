import os
import re
import random
import sys
import urllib
import xbmc
import xbmcaddon
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

tvrage_key = 'VBp9BuIr5iOiBeWCFRMG'
youtube_key = 'AI39si4DkJJhM8cm7GES91cODBmRR-1uKQuVNkJtbZIVJ6tRgSvNeUh4somGAjUwGlvHFj3d0kdvJdLqD0aQKTh6ttX7t_GjpQ'
bandsintown_apikey = 'xbmc_open_source_media_center'
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))


def GetXKCDInfo():
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    items = []
    for i in range(0, 10):
        try:
            base_url = 'http://xkcd.com/'
            url = '%i/info.0.json' % random.randrange(1, 1190)
            results = Get_JSON_response(base_url, url)
            item = {'Image': results["img"],
                    'Title': results["title"],
                    'Description': results["alt"]}
            items.append(item)
        except:
            log("Error when setting XKCD info")
    return items


def GetCandHInfo():
    count = 1
    images = []
    for i in range(1, 30):
        try:
            base_url = 'http://www.explosm.net/comics/'
            url = '%i/' % random.randrange(1, 3128)
            results = Get_JSON_response(base_url, url)
        except:
            log("Error when fetching CandH data from net")
        if response:
            regex = ur'src="([^"]+)"'
            matches = re.findall(regex, results)
            if matches:
                for item in matches:
                    if item.startswith('http://www.explosm.net/db/files/Comics/'):
                        dateregex = '[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]'
                        datematches = re.findall(dateregex, results)
                        newitem = {'Image': item,
                                   'Title': datematches[0]}
                        images.append(newitem)
                        count += 1
              #  wnd.setProperty('CyanideHappiness.%i.Title' % count, item["title"])
                if count > 10:
                    break
    return images


def GetFlickrImages():
    images = []
    results = ""
    try:
        base_url = 'http://pipes.yahoo.com/pipes/pipe.run?'
        url = '_id=241a9dca1f655c6fa0616ad98288a5b2&_render=json'
        results = Get_JSON_response(base_url, url)
    except:
        log("Error when fetching Flickr data from net")
    count = 1
    if results:
        for item in results["value"]["items"]:
            image = {'Background': item["link"]}
            images.append(image)
            count += 1
    return images


def GetYoutubeVideos(jsonurl, prefix=""):
    results = []
    try:
        results = Get_JSON_response("", url)
    except:
        log("Error when fetching JSON data from net")
    count = 1
    log("found youtube vids: " + jsonurl)
    videos = []
    if results:
        try:
            for item in results["value"]["items"]:
                video = {'Thumb': item["media:thumbnail"][0]["url"],
                         'Media': ConvertYoutubeURL(item["link"]),
                         'Play': "PlayMedia(" + ConvertYoutubeURL(item["link"]) + ")",
                         'Title': item["title"],
                         'Description': item["content"]["content"],
                         'Date': item["pubDate"]}
                videos.append(video)
                count += 1
        except:
            for item in results["feed"]["entry"]:
                for entry in item["link"]:
                    if entry.get('href', '').startswith('http://www.youtube.com/watch'):
                        video = {'Thumb': "http://i.ytimg.com/vi/" + ExtractYoutubeID(entry.get('href', '')) + "/0.jpg",
                                 'Media': ConvertYoutubeURL(entry.get('href', '')),
                                 'Play': "PlayMedia(" + ConvertYoutubeURL(entry.get('href', '')) + ")",
                                 'Title': item["title"]["$t"],
                                 'Description': "To Come",
                                 'Date': "To Come"}
                        videos.append(video)
                        count += 1
    return videos


def GetYoutubeSearchVideos(search_string="", hd="", orderby="relevance", time="all_time"):
    results = []
    if hd and not hd == "false":
        hd_string = "&hd=true"
    else:
        hd_string = ""
    search_string = urllib.quote(search_string.replace('"', ''))
    try:
        base_url = 'http://gdata.youtube.com/feeds/api/videos?v=2&alt=json'
        url = '&q=%s&time=%s&orderby=%s&key=%s%s' % (search_string, time, orderby, youtube_key, hd_string)
        results = Get_JSON_response(base_url, url)
    except:
        log("Error when fetching JSON data from net")
    count = 1
    videos = []
    if results:
        for item in results["feed"]["entry"]:
            video = {'Thumb': item["media$group"]["media$thumbnail"][2]["url"],
                     'Play': ConvertYoutubeURL(item["media$group"]["media$player"]["url"]),
                     'Description': item["media$group"]["media$description"]["$t"],
                     'Title': item["title"]["$t"],
                     'Author': item["author"][0]["name"]["$t"],
                     'Date': item["published"]["$t"].replace("T", " ").replace(".000Z", "")}
            videos.append(video)
            count += 1
    return videos


def GetYoutubeUserVideos(userid=""):
    results = []
    userid = urllib.quote(userid.replace('"', ''))
    try:
        base_url = 'https://gdata.youtube.com/feeds/api/users/'
        url = '%s/uploads?v=2&alt=json' % (userid)
        results = Get_JSON_response(base_url, url)
    except:
        log("Error when fetching JSON data from net")
    count = 1
    videos = []
    if results:
        for item in results["feed"]["entry"]:
            video = {'Thumb': item["media$group"]["media$thumbnail"][2]["url"],
                     'Play': ConvertYoutubeURL(item["media$group"]["media$player"]["url"]),
                     'Description': item["media$group"]["media$description"]["$t"],
                     'Title': item["title"]["$t"],
                     'Author': item["author"][0]["name"]["$t"],
                     'Date': item["published"]["$t"].replace("T", " ").replace(".000Z", "")}
            videos.append(video)
            count += 1
    return videos


def HandleBandsInTownResult(results):
    events = []
    for event in results:
        try:
            venue = event['venue']
            artists = ''
            for art in event["artists"]:
                artists += ' / '
                artists += art['name']
                artists = artists.replace(" / ", "", 1)
            event = {'date': event['datetime'].replace("T", " - ").replace(":00", "", 1),
                     'city': venue['city'],
                     'lat': venue['latitude'],
                     'lon': venue['longitude'],
                     'id': venue['id'],
                     'url': venue['url'],
                     'name': venue['name'],
                     'region': venue['region'],
                     'country': venue['country'],
                     #        'artist_mbid': ,
                     #           'status': event['status'],
                     #            'ticket_status': event['ticket_status'],
                     'artists': artists}
            events.append(event)
        except Exception as e:
            log("Exception in HandleBandsInTownResult")
            log(e)
            prettyprint(event)
    return events


def GetArtistNearEvents(Artists):  # not possible with api 2.0
    ArtistStr = ''
    count = 0
  #  prettyprint(Artists)
    for art in Artists:
        artist = art['artist']
        try:
            artist = urllib.quote(artist)
        except:
            artist = urllib.quote(artist.encode("utf-8"))
        if count < 49:
            if len(ArtistStr) > 0:
                ArtistStr = ArtistStr + '&'
            ArtistStr = ArtistStr + 'artists[]=' + artist
            count += 1
    base_url = 'http://api.bandsintown.com/events/search?format=json&location=use_geoip&radius=50&per_page=100&api_version=2.0'
    url = '&%sapp_id=%s' % (ArtistStr, bandsintown_apikey)
    results = Get_JSON_response(base_url, url)
  #   prettyprint(results)
    return HandleBandsInTownResult(results)
    if False:
        log("GetArtistNearEvents: error when getting artist data from " + url)
        log(results)
        return []
