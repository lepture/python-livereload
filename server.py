# coding: utf-8

from livereload import Server, shell

server = Server()
server.watch('docs/*.rst', shell('make html'))
server.serve(root='docs/_build/html', open_url=True)
