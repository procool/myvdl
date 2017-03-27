import logging

logger = logging.getLogger(__name__)

class Extention(object):
    enabled=False

    ##ident="script_ident"

    ## Init plugin:
    @classmethod
    def init(cls, engine):
        pass

    ## Process incomming Message:
    @classmethod
    def process(cls, engine, message, **kwargs):
        return message

