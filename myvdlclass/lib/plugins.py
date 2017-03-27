import os, sys, stat, imp
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class Extention(object):
    def __init__(self, mod, filename, name, enabled=True):
        self.filename = filename
        self.name = name
        self.mod = mod
        self.enabled = enabled
        mod.name = "%s/%s" % (filename, name)

    def __call__(self):
        return self.mod
       
    

class Plugins(object):


    @staticmethod
    def get_plugins_path(dirname):
        pathes = [os.getcwd()] + sys.path
        for path in pathes:
            p = "/".join((path, dirname))
            if os.path.exists(p):
                return p


    def register_plugin(self, name, fpath, is_file):
        dirpath = os.path.dirname(fpath)
        filename, file_extension = os.path.splitext(name)
        if not file_extension in ('.py', '.pyc', ''):
            raise Exception("not a python file")
        if file_extension == '' and is_file:
            raise Exception("not a python module")
        fp, pathname, description = imp.find_module(filename, [dirpath,])
        try:
            mod_ = imp.load_module(filename, fp, pathname, description)
        finally:
            if fp:
                fp.close()
        self.find_extentions(mod_, name=filename)
        return True


    def find_extentions(self, mod_, name=None):
        for extname in dir(mod_):
            extension = getattr(mod_, extname)
            if not hasattr(extension, 'enabled'):
                continue
            if not extension.enabled:
                continue
            self.add_extension(extension, name, extname)


    def add_extension(self, extension, name=None, extname=None):
        logger.info("PLUGIN: Loading extention: %s/%s" % (name, extname))
        self.extensions.append(Extention(extension, name, extname))

    def get_enabled_extensions(self):
        for ext_ in self.extensions:
            if not ext_.enabled:
                continue
            yield ext_


    def get_enabled_extensions_dict(self):
        if hasattr(self, '__extdict'):
            return getattr(self, '__extdict')
        dict_ = {}
        for ext_ in self.get_enabled_extensions():
            name = ext_.mod.name
            if hasattr(ext_.mod, 'ident'):
                name = ext_.mod.ident
                if name in dict_:
                    logger.error("Plugins: %s: Error on saving in dict cache, name %s allready exist!" % (ext_.mod.name, name))
                    continue
            dict_[name] = ext_.mod
        setattr(self, '__extdict', dict_)
        return self.get_enabled_extensions_dict()


    def __getitem__(self, index):
        return self.get_enabled_extensions_dict()[index]

    def __contains__(self, index):
        return index in self.get_enabled_extensions_dict()




    def __init__(self, dirpath='plugins'):
        self.extensions = []

        loaded_files = []
        path_ = self.get_plugins_path(dirpath)
        if path_ is None:
            logger.error('Can not find plugins in directory: %s' % dirpath)
            return None
        sys.path.append(path_)
        for name in os.listdir(path_):
            fpath = os.path.abspath("/".join((path_, name)))
            fstat = os.stat(fpath)

            is_file = True
            if not stat.S_ISREG(fstat.st_mode):
                is_file = False

            filename, file_extension = os.path.splitext(fpath)
            if filename in loaded_files:
                continue
            try: 
                self.register_plugin(name, fpath, is_file)
                loaded_files.append(filename)
            except Exception as err: 
                logger.error('Error on loading plugin: %s: %s' % (name, err))



if __name__ == '__main__':

    ## Get all plugins from 'plugins/' directory: 
    p = Plugins('plugins') 

    ## Print all loaded extentions:
    print p.extensions

    ## Iter by all enabled extentions:
    for ext_ in p.get_enabled_extensions():
        print "Extention:", ext_.filename, ext_.name
        print "Ext. name:", ext_().name
        print "Ext. module:", ext_()
        print

    ## name exist in enabled modules?
    print 'some_ext_name' in p

    ## Fined enabled module by name:
    print p['some_ext_name']

    ## Dict of keys->enabled extention modules
    print p.get_enabled_extensions_dict().keys()


