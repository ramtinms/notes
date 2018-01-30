#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Ramtin Seraj'
SITENAME = 'Random Walk'
SITEURL = 'https://ramtinms.github.io/random-walk/'

PATH = 'content'

DESCRIPTION = 'Random collection of my notes.'

TIMEZONE = 'America/Vancouver'

DEFAULT_LANG = 'en'

THEME = 'themes/pelican-alchemy/alchemy/'

PLUGIN_PATHS = 'plugins/'

PLUGINS = ['ipynb.markup']

IGNORE_FILES = ['.ipynb_checkpoints']

MARKUP = ('md', 'ipynb')

HIDE_AUTHORS = True

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (('Author', 'https://ramtinms.github.io'),)

# Social widget
SOCIAL = (('twitter', 'http://twitter.com/RamtinMehdizade'),
          ('linkedin', 'https://www.linkedin.com/in/ramtin-mehdizadeh-seraj-78a44b42'),
          ('github', 'http://github.com/ramtinms'),)

# google scholar : https://scholar.google.ca/citations?user=BpuPXacAAAAJ&hl=en

TWITTER_USERNAME = "RamtinMehdizade"
DEFAULT_PAGINATION = 4

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
