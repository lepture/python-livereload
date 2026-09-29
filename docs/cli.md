# Command Line Interface

The `livereload` command can be used for starting a live-reloading server, that
serves a directory.

```{command-output} livereload --help

```

It will listen to port 35729 by default, since that's the usual port for
[LiveReload browser extensions].

[livereload browser extensions]: https://livereload.com/extensions/

## Caching

Static files are served with `Cache-Control: no-cache`, so the browser checks
for a new version on every request, and a reload always gets the current file.
Pass `--allow-cache` to leave caching to the browser instead.

```{versionchanged} 2.0.0
`Guardfile` is no longer supported. Write a Python script using the API instead.
```
