# Reference

This page keeps the project details out of the main README.

## Scripts

| File | Purpose | Notes |
| --- | --- | --- |
| `browserbench prep` | Prepares the system for a cleaner run | Installed CLI command |
| `browserbench run` | Main benchmark | Recommended; uses `ioreg` and idle-baseline subtraction |
| `browserbench run-powermetrics` | Alternate benchmark | Uses `powermetrics`; requires `sudo` |
| `browserbench report` | Report command | Auto-detects the BrowserBench CSV schema |
| `sites.txt` | Test site list | One URL per line |

## Data Flow

1. `sites.txt` provides the URLs.
2. A benchmark script opens tabs and simulates browsing.
3. Results are written to a CSV file.
4. A report script summarizes the CSV.

## Supported Browsers

Configured in the benchmark scripts:

- Safari
- Brave
- Chrome
- Firefox
- Edge
- Comet
- ChatGPT Atlas
- Zen

The exact available set depends on what is installed on the machine.

## Automation Model

Browser control is done through AppleScript via `osascript`.

The scripts rotate through realistic browsing behaviors:

- `quick_scan`
- `detailed_read`
- `search_mode`
- `link_navigation`
- `reload_page`
- `zoom_adjust`

Tab switching uses Cmd+number shortcuts.

## Which Workflow to Use

### `browserbench run`

Use this by default.

- Measures total system drain
- Subtracts an idle baseline
- Supports `--duration`
- Better fit for quick browser-to-browser comparisons

### `browserbench run-powermetrics`

Use this when you specifically want `powermetrics`-based sampling.

- Requires `sudo`
- Gives a different measurement path
- Useful as a secondary validation workflow

## Configuration

### Duration

For the default benchmark, use the CLI:

```bash
browserbench run --duration 1200
```

For `run-powermetrics`, set the duration explicitly:

```bash
browserbench run-powermetrics --duration 1200
```

### Browser Selection

Use a comma-separated list:

```bash
browserbench run --browsers chrome,safari
```

### Test Sites

Edit `sites.txt` to change the sites used during the run.

## Adding a New Browser

1. Add the browser to the `BROWSERS` dictionary in both benchmark scripts.
2. Provide:
   - `display_name`
   - `app_name`
   - `process_name`
3. Verify AppleScript interaction works.
4. Verify Cmd+number tab switching works.
5. Run a short focused test:

```bash
browserbench run --browsers your-browser-key --duration 300
```

## Important Benchmark Conditions

- For `browserbench run`, the MacBook must be unplugged.
- Do not actively use the machine during the benchmark.
- The scripts include an idle-baseline period before active browsing.
- Sleep prevention is handled with `caffeinate`.

## Troubleshooting

### Benchmark looks wrong while plugged in

Unplug the MacBook and run again.

### `powermetrics` fails

Use the recommended `browserbench run` workflow, or run `browserbench run-powermetrics` with the required privileges.

### Empty or incomplete results

Check:

- the browsers are installed
- the browser keys are valid
- `sites.txt` contains valid URLs

### Automation acts strangely

AppleScript control can be sensitive to browser state, permissions, and UI focus. Retry with fewer browsers and a shorter duration first:

```bash
browserbench run --browsers safari --duration 300
```

## Related Docs

- Main quick start: [../README.md](../README.md)
- Step-by-step usage: [usage.md](./usage.md)
- Agent-focused notes: [../AGENTS.md](../AGENTS.md)
