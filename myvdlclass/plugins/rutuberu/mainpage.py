import re
import logging
import sys
import json
import subprocess

import xml.etree.ElementTree as ET
#from xml.dom import minidom

from urllib import quote_plus
from copy import deepcopy


from myvdlclass.lib.curl import CUrl, HTTPErrorEx


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MainPage(object):

    def __init__(self, mainobj, *args, **kwargs):
        self.main = mainobj

    def start(self, ident):
        print "RUTUBE Mainpage..."
        info = self.main.get_info(ident)

        print "Title", info["title"]
        print "Description", info["description"]
        print
        print "Embed", info["embed_url"]
        print "TrackID", info["track_id"]
        #print "INFO:", json.dumps(info, indent=4)

        ## Get streams:
        def_tp, route, bl_url = self.main.get_route(info["track_id"])

        flname = "%s.avi" % re.sub("""[\"\,\.\'\s\t\&\;\$\*]+""", "_", info["title"])
        url = None
        ## XML data:
        if def_tp == "default":
            print "XML", route
            root = ET.fromstring(route)
            url = root.find('{http://ns.adobe.com/f4m/2.0}baseURL').text.strip()
            best_brate = 0
            vfile = None
            for fl in root.findall('{http://ns.adobe.com/f4m/2.0}media'):
                br = int(fl.attrib['bitrate'])
                if br > best_brate:
                    best_brate = br
                    vfile = fl
            print "Found video format:", vfile.attrib['width'], "x", vfile.attrib['height'], 
            url += vfile.attrib['href']

        ## Text with urls:
        else:
            for l in route.split('\n'):
                if l.startswith('http'):
                    url = l.strip()

            cmd_ = '''ffmpeg -i "%s" -y "%s"''' % (bl_url, flname)
            print "RUNING COMMAND: ", cmd_
            print
            params = {
                'stderr': subprocess.PIPE,
                'stdout': subprocess.PIPE,
                'shell': True,
            }
            r = subprocess.Popen(cmd_, **params)
            while True:
                l = r.stderr.read(1)
                if len(l) == 0:
                    break
                sys.stdout.write(l)
            print
            print "Download complete!"
            print "Saved as: %s" % flname
            r.stdout.read()
    
            return None

        print "URL: ", url



        ## GEtting video:
        #################
        params = self.main.curl_get_default_params()
        ##params['headers']['Accept'] = "application/json, text/javascript, */*; q=0.01"
        ##params['headers']['Content-Type'] = "application/json"
        answ = CUrl.download(url, 'compressed', **params)
        print "VIDEO", answ

        





