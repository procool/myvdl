import re
import logging
import json

from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .mainpage import MainPage
from .embed import Embed


class RUTubeRU(Extention):

    enabled=True
    ident="rutuberu"

    re_mainpage = re.compile("^http(?:s|):\/\/(?:www\.|)rutube\.ru\/video\/(.*?)(?:\/|)$")
    re_embed = re.compile("^http(?:s|):\/\/(?:www\.|)rutube\.ru\/play\/embed\/(\d+)(?:\/|)$")


    host = "https://rutube.ru"
    cookies_jar_file = "/tmp/myvdl-rutuberu-cookies.jar"

    default_headers = {
        'Host': 'rutube.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }


    @classmethod
    def get_url_re(cls):
        return re.compile('^http(s|):\/\/(www\.|)rutube\.ru')

    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def start(self):

        ## Test for main page url:
        dt = self.re_mainpage.findall(self.url)
        if len(dt) > 0:
            return MainPage(self).start(dt[0])

        ## Test for url is Embed:
        dt = self.re_embed.findall(self.url)
        if len(dt) > 0:
            return Embed(self).start(int(dt[0]))

        print "RUTube: URL %s is not supported!" % self.url




    def curl_get_default_params(self, **kwargs):
        params = {
            'headers': self.default_headers,
            ##'data' : "",
            'cookie': self.cookies_jar_file,
            'cookie-jar': self.cookies_jar_file,
        }
        params.update(kwargs)
        return params



    def get_info(self, ident):
        url = "%s/api/video/%s/" % (self.host, ident)
        params = self.curl_get_default_params()
        params['headers']['Accept'] = "application/json, text/javascript, */*; q=0.01"
        answ = CUrl.download(url, 'compressed', **params)
        return json.loads(answ)


    def get_play_info(self, id):
        url = "%s/api/play/options/%s/?format=json&sqr4374_compat=1&no_404=true" % (self.host, id)
        params = self.curl_get_default_params()
        params['headers']['Accept'] = "application/json, text/javascript, */*; q=0.01"
        params['headers']['Content-Type'] = "application/json"
        answ = CUrl.download(url, 'compressed', **params)
        return json.loads(answ)

    def get_route(self, id):
        pinfo = self.get_play_info(id)
        bal = pinfo["video_balancer"]
        url = None
        #def_tp = "default"
        def_tp = "m3u8"
        if def_tp in bal:
            url = bal[def_tp]

        if url is None:
            url = bal.values()[0]
 

        params = self.curl_get_default_params()
        params['headers']['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ##print "BL URL", url
        answ = CUrl.download(url, 'compressed', **params)
        return def_tp, answ, url



