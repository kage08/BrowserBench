# Usage Guide

This page covers the normal path for running the benchmark and generating a report.

## Recommended Workflow

Use `browserbench run` unless you specifically want `powermetrics`.

Why:

- It is the default workflow for this repo.
- It measures total system drain and subtracts an idle baseline.
- It supports `--duration` for quick comparison runs.
- It does not require running the main benchmark under `sudo`.

## Setup

BrowserBench now installs as a standard CLI app.

```bash
uv tool install .
```

or:

```bash
python -m pip install .
```

## Before You Run

1. Run the environment standardizer:

   ```bash
   browserbench prep
   ```

2. Unplug the MacBook from power.

   `browserbench run` relies on battery discharge measurements. If the machine is plugged in, the numbers will not be useful.

3. Run the preflight checks:

   ```bash
   browserbench doctor
   ```

4. Do not interact with the machine during the benchmark.

5. Make sure the browsers you want to test are installed.

## Run the Recommended Benchmark

Default run:

```bash
browserbench run
```

Run a shorter focused test:

```bash
browserbench run --browsers chrome,safari --duration 300
```

List available browser keys:

```bash
browserbench browsers
```

Run preflight checks only:

```bash
browserbench doctor
```

Generate the report:

```bash
browserbench report
```

Results are written to `browser_power_results2.csv`.

## Alternative Workflow: `powermetrics`

Use this only if you want the older component-power workflow.

Run benchmark:

```bash
browserbench run-powermetrics
```

Run a subset of browsers:

```bash
browserbench run-powermetrics --browsers chrome,firefox,edge
```

Generate the report:

```bash
browserbench report browser_power_results.csv
```

Results are written to `browser_power_results.csv`.

Important:

- `browser_bench.py` uses `powermetrics`.
- `powermetrics` requires `sudo`.

## Typical Session

```bash
browserbench prep
browserbench doctor
browserbench run --browsers chrome,safari --duration 600
browserbench report
```

## Choosing Browsers

By default, the scripts test all configured browsers.

To limit the run, pass a comma-separated list of keys:

```bash
browserbench run --browsers brave,safari,edge
```

Use `browserbench browsers` first if you are unsure which keys are available.

## Test Sites

The scripts read URLs from `sites.txt`.

- One URL per line
- Edit this file to change the browsing mix

## Reports

The report scripts summarize the CSV output and print:

- average power usage
- min and max values
- standard deviation
- simple efficiency comparisons
- rough battery-life estimates

## Next

For repository structure, configuration details, browser support, and troubleshooting, see [reference.md](./reference.md).
