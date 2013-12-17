#!/usr/bin/env python

from livereload import Server, shell

server = Server()
server.watch('style.less', shell('lessc style.less', output='style.css'))
server.serve()
