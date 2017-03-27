import logging
import re

logger = logging.getLogger(__name__)

class Extention(object):
    enabled=False

    ##ident="plugin_ident"

    @classmethod
    def get_url_re(cls):
        return re.compile('^https://some/url')


    def __init__(self, url, *args, **kwargs):
        self.url = url

    def start(self, url):
        pass
