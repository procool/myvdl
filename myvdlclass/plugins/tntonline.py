import re
import logging
import subprocess
import sys

from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class TNTOnline(Extention):

    enabled=True
    ident="tntonline"

    ##re_ident = re.compile("""\<meta name="twitter:player" content="(.*?)"\/\>""")
    re_ident = re.compile("""\<meta name=".*?" content="https:\/\/rutube\.ru\/play\/embed\/(\d+)"\/\>""")

    default_headers = {
        'Host': 'tnt-online.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }


    @classmethod
    def get_url_re(cls):
        return re.compile('^http(s|):\/\/(www\.|)tnt-online\.ru')


    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def start(self):

        params = self.curl_get_default_params()
        answ = CUrl.download(self.url, 'compressed', **params)
        ident = self.re_ident.findall(answ)
        if len(ident) == 0:
            print "Can't find video ident!"
            return None

        print "Found ruTube ident: %s" % ident[0]
        self.engine.find_plugin("https://rutube.ru/play/embed/%s" % ident[0])



    def curl_get_default_params(self, **kwargs):
        params = {
            'headers': self.default_headers,
        }
        params.update(kwargs)
        return params




