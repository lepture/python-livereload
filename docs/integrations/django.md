# Django

LiveReload provides a Django management command: `livereload`. This can be used
to create a live-reloading Django server, that will reload pages.

## Setup

Add `"livereload"` to your `INSTALLED_APPS` in the Django settings module
(typically a `settings.py` file).

## Usage

```
$ python ./manage.py livereload
```

You can optionally provide an port or address-port pair, to specify where the
Django server should listen for requests.

```
$ python ./manage.py livereload 127.0.0.1:8000
```

You can also provide use `-l / --liveport`, for the port the LiveReload server
should listen on. Usually, you don't have to specify this.

To automagically serve static files like the native `runserver` command, you
will need to use something like [Whitenoise].

[whitenoise]: https://github.com/evansd/whitenoise/
