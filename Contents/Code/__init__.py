#MYMOVIES.IT
import datetime, re, time, unicodedata

GOOGLE_JSON_URL = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&q=%s'   #[might want to look into language/country stuff at some point] param info here: http://code.google.com/apis/ajaxsearch/documentation/reference.html
WIKIPEDIA_JSON_URL = 'http://%s.wikipedia.org/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&format=json'
#BING_JSON_URL   = 'http://api.bing.net/json.aspx?AppId=879000C53DA17EA8DB4CD1B103C00243FD0EFEE8&Version=2.2&Query=%s&Sources=web&Web.Count=8&JsonType=raw'

UserAgent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16'

def Start():
  HTTP.CacheTime = CACHE_1WEEK
  
class MymoviesAgent(Agent.Movies):
  name = 'Mymovies'
  # Solo in italiano - it
  languages = [Locale.Language.Italian]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']  
  
  
  def httpRequest(self, url):
    time.sleep(1)
    res = None
    for i in range(5):
      try: 
        res = HTTP.Request(url, headers = {'User-agent': UserAgent})
        #Log("RES: " + str(res))
      except: 
        Log("Error hitting HTTP url:", url)
        time.sleep(1)
        
    return res
      
  def XMLElementFromURLWithRetries(self, url, code_page = None):
    
    res = self.httpRequest(url)
    #Log("HTML.ElementFromString(res): " + str(HTML.ElementFromString(res)))
    #Log("RES: " + res)
    if res:
      if code_page:
        res = str(res).decode(code_page)
      return HTML.ElementFromString(res)
    return None
  
  def getGoogleResult(self, url):
    res = JSON.ObjectFromURL(url)
    if res['responseStatus'] != 200:
      res = JSON.ObjectFromURL(url, cacheTime=0, sleep=0.5)
    return res
  
  def search(self, results, media, lang):
  
    if media.primary_metadata.year:
      searchYear = ' (' + str(media.primary_metadata.year) + ')'
    else:
      searchYear = ''
    
    normalizedName = String.StripDiacritics(media.primary_metadata.title)
    GOOGLE_JSON_QUOTES = GOOGLE_JSON_URL % String.Quote('"' + normalizedName + searchYear + '"', usePlus=True) + '+site:mymovies.it'
    GOOGLE_JSON_NOQUOTES = GOOGLE_JSON_URL % String.Quote(normalizedName + searchYear, usePlus=True) + '+site:mymovies.it'
    GOOGLE_JSON_NOSITE = GOOGLE_JSON_URL % String.Quote(normalizedName + searchYear, usePlus=True) + '+mymovies.it'
    
    for s in [GOOGLE_JSON_QUOTES, GOOGLE_JSON_NOQUOTES, GOOGLE_JSON_NOSITE]:
      #if s == GOOGLE_JSON_QUOTES and (media.name.count(' ') == 0 or media.name.count('&') > 0 or media.name.count(' and ') > 0):
        # no reason to run this test, plus it screwed up some searches
        #continue
      jsonObj = self.getGoogleResult(s)  
      if jsonObj['responseData'] != None:
        jsonObj = jsonObj['responseData']['results']
        if len(jsonObj) > 0:
          url = jsonObj[0]['unescapedUrl']
          if url.count('mymovies.it') > 0:
            Log(" url mymovies.it: " + url)
            score = 100
            Log(" url finale: " + url + "score" + str(score))
            results.Append(MetadataSearchResult( id = url, score = score))
        
  def update(self, metadata, media, lang):
    Log("titolo: " + media.title + "  metadata.id: " + metadata.id)
    page =  self.XMLElementFromURLWithRetries(metadata.id)
        
    if page:
      
        summary = page.xpath('//div[@id="recensione"]/table/tr/td/p/text()')
        
        #Alternative with decode don't work
        #summary = str(page.xpath('//div[@id="recensione"]/table/tr/td/p/text()'))
        #summary2=summary2.lstrip('[u\"\\rn')
        #summary2=summary2.lstrip()
        # squeeze multiple spaces
        #summary2 = re.sub(' {2,}', ' ', summary2)
        
        htmlcodes = ['&Aacute;', '&aacute;', '&Agrave;', '&Acirc;', '&agrave;', '&Acirc;', '&acirc;', '&Auml;', '&auml;', '&Atilde;', '&atilde;', '&Aring;', '&aring;', '&Aelig;', '&aelig;', '&Ccedil;', '&ccedil;', '&Eth;', '&eth;', '&Eacute;', '&eacute;', '&Egrave;', '&egrave;', '&Ecirc;', '&ecirc;', '&Euml;', '&euml;', '&Iacute;', '&iacute;', '&Igrave;', '&igrave;', '&Icirc;', '&icirc;', '&Iuml;', '&iuml;', '&Ntilde;', '&ntilde;', '&Oacute;', '&oacute;', '&Ograve;', '&ograve;', '&Ocirc;', '&ocirc;', '&Ouml;', '&ouml;', '&Otilde;', '&otilde;', '&Oslash;', '&oslash;', '&szlig;', '&Thorn;', '&thorn;', '&Uacute;', '&uacute;', '&Ugrave;', '&ugrave;', '&Ucirc;', '&ucirc;', '&Uuml;', '&uuml;', '&Yacute;', '&yacute;', '&yuml;', '&copy;', '&reg;', '&trade;', '&euro;', '&cent;', '&pound;', '&lsquo;', '&rsquo;', '&ldquo;', '&rdquo;', '&laquo;', '&raquo;', '&mdash;', '&ndash;', '&deg;', '&plusmn;', '&frac14;', '&frac12;', '&frac34;', '&times;', '&divide;', '&alpha;', '&beta;', '&infin']
        funnychars = ['\xc1','\xe1','\xc0','\xc2','\xe0','\xc2','\xe2','\xc4','\xe4','\xc3','\xe3','\xc5','\xe5','\xc6','\xe6','\xc7','\xe7','\xd0','\xf0','\xc9','\xe9','\xc8','\xe8','\xca','\xea','\xcb','\xeb','\xcd','\xed','\xcc','\xec','\xce','\xee','\xcf','\xef','\xd1','\xf1','\xd3','\xf3','\xd2','\xf2','\xd4','\xf4','\xd6','\xf6','\xd5','\xf5','\xd8','\xf8','\xdf','\xde','\xfe','\xda','\xfa','\xd9','\xf9','\xdb','\xfb','\xdc','\xfc','\xdd','\xfd','\xff','\xa9','\xae','\u2122','\u20ac','\xa2','\xa3','\u2018','\u2019','\u201c','\u201d','\xab','\xbb','\u2014','\u2013','\xb0','\xb1','\xbc','\xbd','\xbe','\xd7','\xf7','\u03b1','\u03b2','\u221e']
        newtext = ''
        for char in summary:
          if char not in funnychars:
            newtext = newtext + char
          else:
            newtext  = newtext + htmlcodes[funnychars.index(char)]
        newtext=str(newtext).lstrip()
        
        Log("Newtext: " + str(newtext))
        metadata.summary = newtext