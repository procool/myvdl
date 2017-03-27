import sys

from myvdlclass.lib.plugins import Plugins


class myVDL(object):

    def __init__(self):

        ## Get all interface plugins:
        try:
            self.plugins  = Plugins('myvdlclass/plugins/')
        except Exception as err:
            logger.info('Can not fined any interface plugins in your work directory: myvdl/plugins/')
            self.plugins = {}

        self.urls = []

        ## Try initialize processing plugins:
        for plugin_ in self.plugins.get_enabled_extensions_dict().keys():
            plug = self.plugins[plugin_]
            if not hasattr(plug, 'get_url_re') or not hasattr( getattr(plug, 'get_url_re'), '__call__'):
                continue
            
            self.urls.append((getattr(plug, 'get_url_re')(), plug,))
            
    def cli(self):
        try:
            url = sys.argv[1]
        except Exception as err:
            print ""
            print "FATAL: no url!"
            print "Usage: %s URL\n" % sys.argv[0]
            sys.exit(1)

        for url_ in self.urls:
            f = url_[0].findall(url)
            if isinstance(f, list) and len(f) > 0:
                url_[1](url).start()
                break
                


