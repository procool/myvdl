import json
import re
import logging
import sys
from urllib import quote_plus
from copy import deepcopy


from myvdlclass.plugins.base import Extention
from myvdlclass.lib.curl import CUrl, HTTPErrorEx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class USCLab(Extention):

    enabled=True
    ident="usclab"

    host = "https://www.usclub.ru"
    url_login = "%s/user/login" % host

    re_login = re.compile("""<li class="u-name">.*?<a href="/user/view">(.*?)</a>""")

    cookies_jar_file = "/tmp/myvdl-usclab-cookies.jar"

    default_headers = {
        'Host': 'www.usclub.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    @classmethod
    def get_url_re(cls):
        return re.compile('^https://www.usclub.ru/lecture/item')


    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.curl = ""
        self.setup()


    def setup(self):
        #curl = raw_input("Enter curl code: ")
        self.curl = re.sub('chop/segment-(.*?)\.m4s', 'chop/segment-%s.m4s', self.url)

        #src_name = "%s.orig.m4s" % name
        #dst_name = "%s.avi" % name


    def login(self):
        login  = raw_input("Login: ")
        passwd = raw_input("Password: ")

        login = quote_plus(login)
        passwd = quote_plus(passwd)
        kwargs = {
            'headers': self.default_headers,
            'data' : "LoginForm%5Busername%5D=" + login + "&LoginForm%5Bpassword%5D=" + passwd,
	    'cookie': self.cookies_jar_file,
            'cookie-jar': self.cookies_jar_file,
            'dump-header': 'testheader',
        }

        print "LOGIN", 
        answ = CUrl.download(self.url_login, 'compressed', **kwargs)
        
    

    def get_index(self):

        kwargs = {
            'headers' : self.default_headers,
            'cookie-jar': self.cookies_jar_file,
	    'cookie': self.cookies_jar_file,
        }

        while True:
            answ = CUrl.download(self.url, 'compressed', **kwargs)

            ## Not authed:
            if len(re.findall("""LoginForm_username""", answ)) > 0:
                self.login()
                continue

            a_ = re.sub("\n+", " ", answ)
            uname = self.re_login.findall(a_)
            if len(uname) > 0:
                return uname[0], answ


    def start(self):
        uname, answ = self.get_index()
        print "User: ", uname

        ## Loading lecture code:
        try: 
            lecture_code = int(re.findall("""loadLectureCode\('(\d+)', 'code'\);""", answ)[0]);
        except Exception as err: 
            print "Wrong lecture code!"
            raise err

        lcode_kwargs = {
            'headers' : self.default_headers,
            'cookie': self.cookies_jar_file,
            'data': """id=%s&type=code""" % lecture_code,
        }
        answ = CUrl.download("%s/lecture/loadCode" % self.host, 'compressed', **lcode_kwargs)
        try:
            jcode = json.loads(answ)['code']
        except Exception as err:
            print "Can't encode JSON of handler: /lecture/loadCode"
            raise err
        try: 
            urls = re.findall(r'<iframe src="(.*?)"', jcode)

            ## Get all videos from page:
            for id, url in enumerate(urls):
                self.get_video(id, url)
        except Exception as err:
            print "Can't find video config url!"
            raise err



    ## Load video by founded url:
    def get_video(self, id, url):

        vkwargs = {
            'headers' : self.default_headers,
        }
        ##del vkwargs['headers']['DNT']
        vkwargs['headers']['Host'] = 'player.vimeo.com'
        vkwargs['headers']['Referer'] = self.url
        vdata_s = CUrl.download(url, 'compressed', **vkwargs)

        ## Here, by regexps we can find ids of video and audio tracks:

        #try:
        #    v_ts = re.findall("""https:\/\/(.*?).vimeocdn.com\/(\d+)-(.*?)\/(\d+)\/video\/""", vdata_s)[0]
        #except Exception as err:
        #    print "Can't find video idents!"
        #    raise err
        ##a_ts = re.findall("""https:\/\/(.*?).vimeocdn.com\/(\d+)-(.*?)\/(\d+)\/audio\/""", vdata_s)

        try:
            v_data = re.findall("""function\(e,a\){var t={"cdn_url".*?request":(.*?),"player_url":""", vdata_s)[0]
            v_data = json.loads(v_data)
        except Exception as err:
            print "Can't find video config data!"
            raise err

        #print "VTS", v_ts
        #print
        #print "VDATA", json.dumps(v_data, indent=4)


        """
        ## Download as segments:

        ## Check for separate audio & video:
        separate_av = False
        if "separate_av" in v_data["files"]["dash"] and v_data["files"]["dash"]["separate_av"]:
            separate_av = True


        ## Get video url:
        murl = None
        default_cdn = v_data["files"]["dash"]["default_cdn"]
        for cdn, d in v_data["files"]["dash"]["cdns"].items():
            if "skyfire" in cdn:
                if separate_av:
                    murl = re.sub(r"sep\/video\/\d+(.*?)$", "sep/", d["url"])
                else:
                    murl = re.sub(r"video\/\d+(.*?)$", "video/", d["url"])
                break
        if murl is None:
            print "Wrong video config"
            return None

        url_a = None
        if separate_av:
            murl += "video/"
            url_a = murl + "audio/"

        ## Get high'st quality:
        stream_id = [0, None]
        for stream in v_data["files"]["dash"]["streams"]:
            try: qa = int(re.findall("^(\d+)p", stream["quality"])[0])
            except: continue
            if qa > stream_id[0]:
                stream_id[0] = qa
                stream_id[1] = str(stream["id"])

        logging.info("Selected quality: %s" % stream_id[0])

        murl += stream_id[1] + '/chop/segment-%s.m4s'
        if separate_av:
            url_a += stream_id[1] + '/chop/segment-%s.m4s'

        print "DOWNLOAD %s: url:" % separate_av, murl
        """

        ##################################
        ## Download as completly mp4 file:

        ## Get high'st quality:
        stream_id = [0, None]
        for stream in v_data["files"]["progressive"]:
            try: qa = int(re.findall("^(\d+)p", stream["quality"])[0])
            except: continue
            if qa > stream_id[0]:
                stream_id[0] = qa
                stream_id[1] = stream["url"]


        print "Found quality: %sp" % stream_id[0]
        print "Download url: ", stream_id[1]

        ext_ = re.sub("\?(.*)$", "", stream_id[1])
        ext_ = re.findall("\/.*?\.([^.]+)$", ext_)[0]
        
        name = re.findall("item/(.*?)$", self.url)[0]
        flname = "%s_%s.%s" % (name, id, ext_)
        print "Save as: %s" % flname

        vkwargs['output'] = flname
        del vkwargs['headers']['Host']
        vkwargs['print_status'] = True
        CUrl.download(stream_id[1], **vkwargs)
        



        






          





