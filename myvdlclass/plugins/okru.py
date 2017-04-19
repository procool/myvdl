import re
import logging
import subprocess
import sys
import lxml
        
from urllib import quote_plus

from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class OKRU(Extention):

    enabled=True
    ident="okru"

    ##re_ident = re.compile("""\<meta name="twitter:player" content="(.*?)"\/\>""")
    re_ident = re.compile("""\<meta name=".*?" content="https:\/\/rutube\.ru\/play\/embed\/(\d+)"\/\>""")

    cookies_jar_file = "/tmp/myvdl-okru-cookies.jar"

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
        return re.compile('^http(s|):\/\/(www\.|m\.|)ok\.ru\/video\/')


    def __init__(self, url, engine, *args, **kwargs):
        self.url = url
        self.engine = engine

    def find_ident(self):

        """

<div id="content">
<div id="mvplayer_cont" class="mvplayer_cont mvinternal_true">
<a class="outLnk fll vdo tbcont js-click" data-video="{&quot;videoPosterSrc&quot;:&quot;//pimg.mycdn.me/getImage?url=http%3A%2F%2Fi.mycdn.me%2Fimage%3Fid%3D837688717548%26bid%3D837688717548%26t%3D50%26plc%3DWEB%26tkn%3D*o1o6MztVYnczqoX2-xLYx79QfRo\u0026type=VIDEO_S_368\u0026signatureToken=05-N7j63PIV4hNj-20CPVg&quot;,&quot;errorCheckUrl&quot;:&quot;&quot;,&quot;externalStats&quot;:{},&quot;videoSrc&quot;:&quot;https://m.ok.ru/dk?st.cmd=moviePlaybackRedirect\u0026st.sig=8e429bbed3b9e3c0033ebd9369f618c449860320\u0026st.mq=1\u0026st.mvid=94020831980\u0026st.ip=94.25.183.194\u0026st.exp=1492294820293\u0026_prevCmd=movieLayer\u0026tkn=2182&quot;,&quot;movieId&quot;:&quot;94020831980&quot;,&quot;providerName&quot;:&quot;UploadedODKL&quot;}" data-embedclass="yt_layer" data-objid="94020831980" href="https://m.ok.ru/dk?st.cmd=moviePlaybackRedirect&amp;st.sig=2eb2e6ec26d87a39ebb47f03d9b938d0a9448519&amp;st.mq=1&amp;st.mvid=94020831980&amp;st.ip=94.25.183.194&amp;st.exp=1492294820294&amp;_prevCmd=movieLayer&amp;tkn=6577" data-autoplay="1"><img src="//pimg.mycdn.me/getImage?url=http%3A%2F%2Fi.mycdn.me%2Fimage%3Fid%3D837688717548%26bid%3D837688717548%26t%3D50%26plc%3DWEB%26tkn%3D*o1o6MztVYnczqoX2-xLYx79QfRo&amp;type=VIDEO_S_368&amp;signatureToken=05-N7j63PIV4hNj-20CPVg" class="vdo thumb"><div class="vdo playb"></div><div class="vd_tmr">1:43:25</div></a>
</div>
</div>


        https://m.ok.ru/dk?st.cmd=moviePlaybackRedirect&st.sig=2eb2e6ec26d87a39ebb47f03d9b938d0a9448519&st.mq=1&st.mvid=94020831980&st.ip=94.25.183.194&st.exp=1492294820294&_prevCmd=movieLayer&tkn=6577
        https://m.ok.ru/dk?st.cmd=moviePlaybackRedirect&st.mq=1&st.mvid=94020831980&st.exp=1492294820294
        https://m.ok.ru/dk?st.cmd=moviePlaybackRedirect&st.mq=1&st.mvid=94020831980

from lxml.html import parse
page = parse('http://habrahabr.ru/').getroot()
hrefs = page.cssselect("a.topic")
for row in hrefs:
    print row.get("href")

        """

        dt = re.findall("^http(?:s|):\/\/(?:www\.|m\.|)ok.ru/video/(\d+)(?:\/|)$", self.url)
        if len(dt) > 0:
            return dt[0]
        return None

        
    def start(self):

        ident = self.find_ident()
        if ident is None:
            print "OK.RU: Unsupported url!"
            return None

        m_url = "https://m.ok.ru/video/" + ident
        params = self.curl_get_default_params()
        """
curl 'https://m.ok.ru/video/94020831980' -H 'Host: m.ok.ru' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Cookie: bci=-1960779979281354807; landref=ydalenka.ru; __dc=on; SERVERID=bcf0ec7670cbc75ebc8f0ce9d1a73887|WO/8C; TimezoneOffset=-180; ClientTimeDiff=-539; ClientTimeStr=14_3_2017_1_20_19; DCAPS=dpr%5E1%7Cvw%5E1600%7Csw%5E1600%7C' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'Cache-Control: max-age=0'
        """
        params["headers"]["Host"] = 'm.ok.ru'

        try:
            answ = CUrl.download(m_url, 'compressed', **params)
        except Exception as err:
            print "OK.RU: Can't load mobile video page! May be wrong url?"
            return None

        try:
            dt = re.findall('\<div id\=\"content\"(?:.*?)\<div id=\"mvplayer_cont\"(?:.*?)data\-video(?:.*?)href=\"(.*?)\"', answ)
            url = dt[0]
        except Exception as err:
            print "MAIL.RU: No video found!"

        extention = "mp4"

        flname = "%s.%s" % (ident, extention)
        print "OK.RU: DOWNLOADING:", url
        params = self.curl_get_default_params()
        CUrl.download(url, 'globoff', 'compressed', L=True, print_status=True, output=flname, **params)
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




