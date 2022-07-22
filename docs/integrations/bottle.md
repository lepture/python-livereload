# bottle.py

LiveReload's {any}`livereload.Server` class can be used directly with
`bottle.py`.

## Setup

Use the `livereload.Server` to serve the application.

## Usage

```python
import bottle
from livereload import Server

bottle.debug(True)  # debug mode is required for templates to be reloaded

app = Bottle()

server = Server(app)
server.watch(...)
server.serve()
```
