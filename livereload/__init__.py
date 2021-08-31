"""Reload webpages on changes, without hitting refresh in your browser.
"""

__version__ = '2.6.3'
__author__ = 'Hsiaoming Yang <me@lepture.com>'
__homepage__ = 'https://github.com/lepture/python-livereload'

from .server import Server, shell

__all__ = ('Server', 'shell')
