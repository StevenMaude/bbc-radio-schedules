# bbc-radio-schedules :radio::spiral_notepad:

Unofficial Python API and CLI for BBC radio station schedules.

## Requirements

* Python 3.11 or newer
* [uv](https://docs.astral.sh/uv/) for local development

## Install

Install the package with `uv` or `pip`:

```sh
uv tool install git+https://github.com/StevenMaude/bbc-radio-schedules
```

```sh
pip install git+https://github.com/StevenMaude/bbc-radio-schedules
```

## Development

Set up the project environment with:

```sh
uv sync --dev
```

Run the tests with:

```sh
uv run python -m unittest discover tests/
```

## API client

There are four main classes:

* `Stations`
  * Construct via `bbcradio.Stations()`.
* `Station`
  * Construct via `Stations().select("BBC Radio 2")`.
* `Schedule`
  * Construct via `bbcradio.Schedule()`, passing in a `Station()` and a
    date string in the `YYYY-MM-DD` format.
* `Programme`
  * Used to store details for a programme; a `Schedule()` contains a
    list of `Programme()`.

See the [CLI client](bbcradio/cli.py) for an example.

## CLI client

After installing the package, run one of the entry points:

```sh
bbcradio --help
bbcradio stations
bbcradio schedule "BBC Radio 2" "2026-05-20"
```
