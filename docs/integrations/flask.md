# Flask

LiveReload's {any}`livereload.Server` class can be used directly with Flask.

## Setup

Use the `livereload.Server` to serve the application.

## Usage

```python
from livereload import Server

app = create_app()
app.debug = True  # debug mode is required for templates to be reloaded

server = Server(app.wsgi_app)
server.watch(...)
server.serve()
```
