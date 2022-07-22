# Command Line Interface

The `livereload` command can be used for starting a live-reloading server, that
serves a directory.

```{command-output} livereload --help

```

It will listen to port 35729 by default, since that's the usual port for
[LiveReload browser extensions].

[livereload browser extensions]: https://livereload.com/extensions/

```{versionchanged} 2.0.0
`Guardfile` is no longer supported. Write a Python script using the API instead.
```
