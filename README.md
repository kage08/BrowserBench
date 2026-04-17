# BrowserBench

Measure and compare real-world browser power usage on macOS.

BrowserBench is installable as a normal CLI app. After install, users run `browserbench` directly instead of cloning the repo and invoking individual scripts.

## Install

With `uv`:

```bash
uv tool install .
```

With `pip`:

```bash
python -m pip install .
```

For local development without a global install:

```bash
uv run browserbench --help
```

For a local editable install during development:

```bash
uv pip install -e .
```

## Quick Start

1. Prepare the Mac for a cleaner run:

   ```bash
   browserbench prep
   ```

2. Unplug the MacBook from power.

   The default `ioreg` workflow measures battery discharge and requires the machine to be running on battery.

3. Run the preflight check:

   ```bash
   browserbench doctor
   ```

4. Run the benchmark:

   ```bash
   browserbench run
   ```

5. Generate the report:

   ```bash
   browserbench report
   ```

## Most Useful Commands

Run only a few browsers for a shorter test:

```bash
browserbench run --browsers chrome,safari --duration 300
```

List the configured browser keys:

```bash
browserbench browsers
```

Run the preflight checks without starting a benchmark:

```bash
browserbench doctor
```

Use the older `powermetrics` workflow instead:

```bash
browserbench run-powermetrics
browserbench report browser_power_results.csv
```

Note: `browserbench run-powermetrics` uses `powermetrics`, which requires `sudo`.

## `uvx` Usage

Once the package is published to PyPI:

```bash
uvx browserbench --help
```

If you want to test the public GitHub repo before publishing, `uvx` can also install from a Git URL:

```bash
uvx --from git+https://github.com/<owner>/<repo> browserbench --help
```

Replace `<owner>/<repo>` with the actual repository path.

## Publishing Notes

The package metadata is ready for a normal Python release flow. Before publishing to PyPI, run one full install/build check in a normal networked environment so `hatchling` can be resolved and the release artifacts can be validated end to end.

A typical release flow will look like:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

## Where Everything Went

- Setup, running, and report workflows: [docs/usage.md](./docs/usage.md)
- Files, workflows, customization, and troubleshooting: [docs/reference.md](./docs/reference.md)
- AI-agent-specific repo notes: [AGENTS.md](./AGENTS.md)

## What You Need

- macOS
- `uv` or `pip`
- At least one supported browser installed
- A MacBook running on battery for the default `browserbench run` workflow

## Output Files

- `browser_power_results2.csv`: results from `browserbench run`
- `browser_power_results.csv`: results from `browserbench run-powermetrics`

If you are new to the project, start with [docs/usage.md](./docs/usage.md).
