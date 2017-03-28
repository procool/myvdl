import re
import logging
import subprocess
import sys

from myvdlclass.lib.curl import CUrl, HTTPErrorEx

from .mainpage import MainPage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Embed(object):

    re_ident = re.compile("""\<link rel="canonical" href="https://rutube.ru\/video\/(.*?)\/"\/\>""")


    def __init__(self, mainobj, *args, **kwargs):
        self.main = mainobj

    def start(self, id):
        print "RUTUBE Embed..."

        url = "%s/play/embed/%s" % (self.main.host, id)
        params = self.main.curl_get_default_params()
        answ = CUrl.download(url, 'compressed', **params)
        ident = self.re_ident.findall(answ)
        if len(ident) == 0:
            print "Can't find video ident!"
            return None

        return MainPage(self.main).start(ident[0])


