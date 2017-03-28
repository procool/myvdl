import re
import logging
import subprocess
import sys

from myvdlclass.plugins.base import Extention

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class YouTube(Extention):

    enabled=True
    ident="youtube"

    @classmethod
    def get_url_re(cls):
        return re.compile('^http(s|):\/\/(www\.|)youtu(be\.com|\.be)')


    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def start(self):
        print "It would be better to use youtube-dl software!"
        cmd_ = "youtube-dl %s" % self.url

        logger.info("YOUTUBE-DL: %s" % cmd_)
        params = {
            'stderr': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'shell': True,
        }
        r = subprocess.Popen(cmd_, **params)
        while True:
            l = r.stdout.read(1)
            if len(l) == 0:
                break
            sys.stdout.write(l)

        print "Download complete!"



