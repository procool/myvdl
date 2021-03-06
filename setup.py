#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set expandtab shiftwidth=4:
#
# Copyright (C) 2015 Progroup Software
# All rights reserved.
#

from setuptools import setup, find_packages
from os.path import join, dirname
from os import chdir, walk
import myvdlclass.version
import sys


from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False


if len(sys.argv) and not dirname(sys.argv[0]) == '':
	chdir( dirname(sys.argv[0]) )




setup(
	author = 'procool',
	author_email = 'ya.procool@ya.ru',
	license = 'BSD 2 Clause',
	#url = 'http://procool.ru/',
	#download_url = 'http://procool.ru/download/',

	name = "myvdl",
	version = myvdlclass.version.__version__,
	packages = find_packages(),
	description=open(join(dirname(__file__), 'README')).readline(),
	long_description=open(join(dirname(__file__), 'README')).read(),
	    
	entry_points={
		'console_scripts':
		[
			'myvdl = myvdlclass.scripts.myvdl:main',
		],
	},

    
	install_requires=[
		'setuptools', 
		'gevent', 
                'lxml',
                'cssselect',
	],

        include_package_data=True,
        distclass=BinaryDistribution,
)
