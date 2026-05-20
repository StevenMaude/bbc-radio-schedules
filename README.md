# bbc-radio-schedules :radio::spiral_notepad:

An unofficial Python client and CLI for BBC radio station schedules.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for development workflows

## Install

Install the package with `pip`:

```sh
pip install git+https://github.com/StevenMaude/bbc-radio-schedules
```

For local development, create an environment and install the project with `uv`:

```sh
uv sync
```

## API client

There are four main classes:

- `bbcradio.Stations()` retrieves the available stations.
- `Stations.select(name)` returns a `bbcradio.Station`.
- `bbcradio.Schedule(station, "YYYY-MM-DD")` retrieves a schedule.
- `bbcradio.Programme` stores details for an individual programme.

See the [CLI client](bbcradio/cli.py) for a complete example.

## CLI client

After installing the package, run:

```sh
bbcradio_cli -h
bbcradio_cli stations
bbcradio_cli schedule "BBC Radio 1" "2026-05-19"
```

## Development

Run the checks with `uv`:

```sh
uv run black --check .
uv run python -m unittest discover tests
```

The test suite includes a live BBC integration test. It automatically skips
when the BBC site is unavailable from the current environment.
