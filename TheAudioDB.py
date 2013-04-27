import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import *
import urllib

AudioDB_apikey = '58353d43204d68753987fl'
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def GetAudioDBData(url = "", cache_days = 14):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://www.theaudiodb.com/api/v1/json/%s/%s' % (AudioDB_apikey, url)
        response = GetStringFromUrl(url)
        results = json.loads(response)
        log("look here")
        save_to_file(results,filename,Addon_Data_Path)
        return results
        
def HandleAudioDBAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    prettyprint(results)
    if 'album' in results and results['album']:
        for album in results['album']:
            if 'strDescriptionEN' in album:
                Description = album['strDescriptionEN']
            elif 'strDescription' in album:
                Description = album['strDescription']
            else:
                Description = ""
            album = {'artist': album['strArtist'],
                     'mbid': album['strMusicBrainzID'],
                     'id': album['idAlbum'],
                     'audiodbid': album['idAlbum'],
                     'Description': Description,
                     'Genre': album['strSubGenre'],
                     'thumb': album['strAlbumThumb'],
                     'year': album['intYearReleased'],
                     'Sales': album['intSales'],
                     'name':album['strAlbum']  }
            albums.append(album)
    else:
        log("Error when handling HandleAudioDBAlbumResult results")
    return albums
    
def GetExtendedAudioDBInfo(results):
    artists = []
    log("starting GetExtendedAudioDBInfo")
    if 'artists' in results and results['artists']:
        for artist in results['artists']:
            if 'strBiographyEN' in artist:
                Description = artist['strBiographyEN']
            elif 'strBiography' in artist:
                Description = artist['strBiography']
            else:
                Description = ""
            artist = {'artist': artist['strArtist'],
                     'mbid': artist['strMusicBrainzID'],
                     'Banner': artist['strArtistBanner'],
                     'audiodbid': artist['idArtist'],
                     'Description': Description,
                     'Genre': artist['strSubGenre'],
                     'thumb': artist['strArtistThumb'],
                     'Members':artist['intMembers']  }
            artists.append(artist)
    else:
        log("Error when handling GetExtendedAudioDBInfo results")
    return artists[0]
    
    
    
def GetDiscography(search_string):
    url = 'searchalbum.php?s=%s' % (urllib.quote_plus(search_string))
    results = GetAudioDBData(url)
    if True:
        return HandleAudioDBAlbumResult(results)
    else:
        return []
        
def GetArtistDetails(search_string):
    url = 'search.php?s=%s' % (urllib.quote_plus(search_string))
    results = GetAudioDBData(url)
    prettyprint(results)
    if True:
        return GetExtendedAudioDBInfo(results)
    else:
        return []
        
        
def GetAlbumDetails(audiodbid):
    url = 'album.php?m=%s' % (audiodbid)
    results = GetAudioDBData(url)
    prettyprint(results)
    if True:
 #       return GetExtendedAlbumInfo(results)
  #  else:
        return []
        
