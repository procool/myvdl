import re
import logging
import subprocess
import sys
import json
import lxml.html
        
from urllib import quote_plus

from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class MyVIRU(Extention):

    enabled=True
    ident="myviru"

    cookies_jar_file = "/tmp/myvdl-myviru-cookies.jar"

    default_headers = {
        #'Host': 'ok.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }



    @classmethod
    def get_url_re(cls):
        return re.compile('^http(s|):\/\/(www\.|)myvi\.ru\/watch\/')

    #http://myvi.ru/player/api/Video/Get/ol5q-Pb64zKd4iQxsSpUNpWbVQUDKTILgskI9IIHGikCZ0x6fsrxtPnrYbLT_r6pU0?sig=eeec4dbaf343e9d5e515a5b11e4f9b43&referer=http%3A%2F%2Fwww.myvi.ru%2Fwatch%2FLqDohJzLfECaY5pcNy6Muw2&ap=True&cl=False


    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def find_iframe(self):
        params = self.curl_get_default_params()
        answ = CUrl.download(self.url, 'globoff', 'compressed', **params)

        page = lxml.html.fromstring(answ)
        href = page.cssselect("#player-container iframe")[0]
        return "http:%s" % href.attrib['src']
        

    def find_data_url(self):
        iframe = self.find_iframe()

        params = self.curl_get_default_params()
        answ = CUrl.download(iframe, 'globoff', 'compressed', **params)
        page = lxml.html.fromstring(answ)
        data = page.cssselect("body script")[0]

        script_ = lxml.html.tostring(data)
        data_url = "http://myvi.ru%s" % re.findall("""dataUrl\:'(.*?)',""", script_)[0]
        return data_url

    def find_video_url(self):
        data_url = self.find_data_url()

        params = self.curl_get_default_params()
        answ = CUrl.download(data_url, 'globoff', 'compressed', **params)
        data = json.loads(answ)
        #print "XXX", json.dumps(data, indent=4)
        video_ = data['sprutoData']['playlist'][0]
        return video_['video'][0]['url'], video_['title']


        
    def start(self):

        url, ident = self.find_video_url()

        extention = "mp4"

        flname = "%s.%s" % (ident, extention)
        print "MYVI.RU: DOWNLOADING:", url
        params = self.curl_get_default_params()
        params['headers']['X-Requested-With'] = 'ShockwaveFlash/23.0.0.205'
        params['headers']['Accept'] = '*/*'
        CUrl.download(url, 'globoff', 'compressed', print_status=True, output=flname, L=True, **params)
        print
        print "Saved as: %s" % flname
        return None


    def curl_get_default_headers(self, **kwargs):
        return dict(self.default_headers.items())

    def curl_get_default_params(self, **kwargs):
        params = {
            'headers': self.curl_get_default_headers(),
            'cookie-jar': self.cookies_jar_file,
            'cookie': self.cookies_jar_file,
        }
        params.update(kwargs)
        return params




