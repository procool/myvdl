import subprocess
import sys
import logging

logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)
logger.setLevel(logging.INFO)


class HTTPErrorEx(Exception):
    pass

class CUrl(object):
    cmd = """/usr/bin/curl '%(url)s' %(args)s %(headers)s"""

    @classmethod
    def download(cls, url, *args, **kwargs):
        try: print_status = kwargs.pop('print_status')
        except: print_status = False

        try: headers = dict(kwargs.pop('headers'))
        except: headers = {}

        cmd_ = cls.cmd % {
            'url': url,
            'args': " ".join(["--%s" % i for i in args]),
            'headers': " ".join( ["-H '%s: %s'" % (k, v) for k, v in headers.items()] ),
        } 

        try: 
            data = kwargs.pop('data')
            cmd_ = "%s --data '%s'" % (cmd_, data)
        except: 
            pass

        try:
            cjar = kwargs.pop('cookie-jar')
            cmd_ = "%s --cookie-jar '%s'" % (cmd_, cjar)
        except:
            pass

        try:
            cookies = kwargs.pop('cookie')
            cmd_ = "%s --cookie '%s'" % (cmd_, cookies)
        except:
            pass

        try:
            dumpheader = kwargs.pop('dump-header')
            cmd_ = "%s --dump-header '%s'" % (cmd_, dumpheader)
        except:
            pass

        try:
            output = kwargs.pop('output')
            cmd_ = "%s --output '%s'" % (cmd_, output)
        except:
            output = None



        logger.info("CURL: %s" % cmd_)
        params = {
            'stderr': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'shell': True,
        }
        #if print_status:
        #    params['stderr'] = sys.stdout.buffer

        r = subprocess.Popen(cmd_, **params)

        if print_status and output is not None:
            while True:
                l = r.stderr.read(1)
                if len(l) == 0:
                    break
                sys.stdout.write(l)

            print "Download complete!"


        buff = r.stdout.read()

        if len(buff) == 0:
            return u""
        if buff == "Bad Request":
            raise HTTPErrorEx("bad_request")
        if buff[1:23] == "No download URL found!":
            raise HTTPErrorEx("not_found")
        return buff

