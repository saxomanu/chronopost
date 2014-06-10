#!/usr/bin/env python

import os
from setuptools import setup

__author__ = 'Florian da Costa <florian.dacosta@akretion.com>'
__version__ = '0.1.0'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	# Basic package information.
	name = 'chronopost_api',
	version = __version__,

	# Packaging options.
	include_package_data = True,

	# Package dependencies.
	install_requires = ['suds'],

	# Metadata for PyPI.
	author = 'Florian da Costa',
	author_email = 'florian.dacosta@akretion.com',
	license = 'GNU AGPL-3',
	url = 'http://github.com/florian-dacosta/chronopost',
    packages=['chronopost_api'],
	keywords = 'chronopost fr label',
	description = 'A library to generation carrier label with Chronopost Fr.',
	long_description = read('README.md'),
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet :: WWW/HTTP :: ?????',
		'Topic :: Internet'
	]
)
