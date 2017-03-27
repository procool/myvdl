# -*- coding: utf-8 -*-

import logging
import re

from base import Extention
from mybot.core.message import Message
from copy import deepcopy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class echoPlugin(Extention):
    """
    This is a text extention ECHO - answers to everybody for any message
    """

    enabled=True

    ident="echo"

    ## Process incomming Message:
    @classmethod
    def process(cls, engine, message, **kwargs):
        if 'nickname' in message.server:
            message.sender = message.server['nickname']
        message.plugin.send(message)
        return message


class my_echoPlugin(Extention):
    """
    This is a text extention my_ECHO - answers to user that send message to bot, e.g.:
    bot_nickname: text

    Bot's nickname must be setted up in settings.SERVERS for selected server 
    as 'nickname' argument, for e.g:
        SERVERS = [
            {
                'type': 'stdin',
                'nickname': 'bot',
            },
        ]
    """

    enabled=True

    ident="myecho"

    re_to = re.compile('^(([\w\dА-Яа-я]+): )')

    ## Process incomming Message:
    @classmethod
    def process(cls, engine, message, **kwargs):

        if not 'nickname' in message.server:
            logger.error('myecho: no "nickname" key in server configuration! %s' % message.server)
            return None
        my_nickname = message.server['nickname']

        to_ = cls.re_to.findall(message.text)

        ## Message to everybody, not for us:
        if len(to_) <= 0:
            return message

        ## Message to another user, not for us:
        if to_[0][1].upper() != my_nickname.upper():
            return message

        ## Message for us, make answer:
        answ_setts = deepcopy(message)
        answ = Message(**answ_setts)
        answ['sender'] = my_nickname
        answ.text = message.sender + ': ' + message.text[len(to_[0][0]):]
        message.plugin.send(answ)
        return None
