# Releasing BrowserBench

This page covers the packaging and publishing workflow for the installed `browserbench` CLI.

## Before Publishing

1. Confirm the package installs cleanly:

   ```bash
   uv pip install -e .
   browserbench --help
   ```

2. Confirm the main user flows still work:

   ```bash
   browserbench browsers
   browserbench doctor
   browserbench report
   ```

## Build

```bash
python -m pip install build twine
python -m build
```

This should produce source and wheel artifacts under `dist/`.

## Validate

```bash
python -m twine check dist/*
```

## Publish

```bash
python -m twine upload dist/*
```

After publishing, users should be able to run:

```bash
uvx browserbench --help
```

or install it normally with:

```bash
python -m pip install browserbench
```

## Notes

- The default benchmark is macOS-only and assumes browser automation through AppleScript.
- `browserbench run` expects the machine to be on battery.
- `browserbench run-powermetrics` requires `sudo`.
