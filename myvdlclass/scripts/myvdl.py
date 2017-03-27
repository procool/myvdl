#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set expandtab shiftwidth=4:

import logging
import os, sys

#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')
logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

logger = logging.getLogger(__name__)

from myvdlclass.lib.core import myVDL


def main():
    myvdl_ = myVDL()
    myvdl_.cli()


if __name__ == '__main__':
    main()
