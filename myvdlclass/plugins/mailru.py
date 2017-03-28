import re
import logging
import subprocess
import sys
import json
        
from urllib import quote_plus

from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class MailRU(Extention):

    enabled=True
    ident="mailru"

    ##re_ident = re.compile("""\<meta name="twitter:player" content="(.*?)"\/\>""")
    re_ident = re.compile("""\<meta name=".*?" content="https:\/\/rutube\.ru\/play\/embed\/(\d+)"\/\>""")

    cookies_jar_file = "/tmp/myvdl-mailru-cookies.jar"

    default_headers = {
        #'Host': 'mail.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }


    @classmethod
    def get_url_re(cls):
        return re.compile('^http(s|):\/\/(www\.|my\.|)mail\.ru')


    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def find_ident(self):

        """
        ## Get by http://zasasa.com/ru/skachat_video_s_mail.ru.php

        ##http://my.mail.ru/video/inbox/www.kristina/29/31.html
        url = "http://videoapi.my.mail.ru/videos/inbox/www.kristina/29/31.json"

        ##https://my.mail.ru/v/thisishorosho_tv/video/_groupvideo/769.html
        url = "http://videoapi.my.mail.ru/videos/v/thisishorosho_tv/_groupvideo/769.json"

        ##https://my.mail.ru/list/xakepx/video/199/283.html
        url = "http://videoapi.my.mail.ru/videos/list/xakepx/199/283.json"

        ##https://my.mail.ru/mail/gromow1981/video/_myvideo/1395.html
        url = "http://videoapi.my.mail.ru/videos/mail/gromow1981/_myvideo/1395.json"

        ##https://my.mail.ru/corp/afisha/video/trailers/15375.html
        url = "http://videoapi.my.mail.ru/videos/corp/afisha/trailers/15375.json"
        """

        url = "http://videoapi.my.mail.ru/videos/"

        dt = re.findall("http(?:s|)://my.mail.ru/video/(.*)\.html$", self.url)
        if len(dt) > 0:
            return url+dt[0]+".json"

        dt = re.findall("http(?:s|)://my.mail.ru/(.*)\.html$", self.url)
        if len(dt) > 0:
            return url+dt[0]+".json"

        return None

        
    def start(self):

        api_url = self.find_ident()
        if api_url is None:
            print "MAIL.RU: Unsupported url!"
            return None

        params = self.curl_get_default_params()
        try:
            answ = CUrl.download(api_url, 'compressed', **params)
            data = json.loads(answ)
            #print "DATA", json.dumps(data, indent=4)
        except Exception as err:
            print "MAIL.RU: Can't load video data, may be wrong url?"
            return None

        flname = "%s" % re.sub("""[\"\,\.\'\s\t\&\;\$\*]+""", "_", data["meta"]["title"])
  
        hq = 0
        url = None
        for v in data["videos"]:
            hq_ = int(v["key"].replace("p", ""))
            if hq_ > hq:
                hq = hq_
                url = v["url"]

        if url is None:
            print "MAIL.RU: No video found!"

        flext = re.findall("""\/\d+\.(.*?)\?""", url)[0]
        flname += ".%s" % flext

        print "MAIL.RU: DOWNLOADING:", url
        CUrl.download(url, 'globoff', 'compressed', print_status=True, output=flname, **params)
        print
        print "Saved as: %s" % flname


    def curl_get_default_params(self, **kwargs):
        params = {
            'headers': self.default_headers,
            'cookie-jar': self.cookies_jar_file,
            'cookie': self.cookies_jar_file,
        }
        params.update(kwargs)
        return params




