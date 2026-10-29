# nuclear

A package that has a mix of nuke related tooling to general 2d pipeline.

## Install

Install the package and its development tools:

```sh
uv sync
```

## Quick start

Run the package module:

```sh
uv run python -m nuclear.main
```
## Documentation development

Preview the documentation locally with live reload:

```sh
uv run mkdocs serve
```

Build the static site into `dist/docs/`:

```sh
uv run mkdocs build
```

This site uses Material for MkDocs and starts in dark mode. Use its built-in palette control to
switch to light mode; your choice is remembered in the browser.
