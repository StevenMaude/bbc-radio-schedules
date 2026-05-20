# bbc-radio-schedules :radio::spiral_notepad:

Implements an unofficial API client in Python and provides an example
command-line client for processing BBC Radio station programme
schedules.

## Requirements

Python 3.11 or later.

## Install

Install with `uv` or `pip`:

```sh
uv pip install git+https://github.com/StevenMaude/bbc-radio-schedules
```

or

```sh
pip install git+https://github.com/StevenMaude/bbc-radio-schedules
```

## Development setup

```sh
uv sync
```

## API client

There are four main classes. These are constructed with very little
input, since the data is retrieved from the BBC site.

* `Stations`
  * Construct via `bbcradio.Stations()`.
* `Station`
  * The `Stations()` `.select()` method constructs a `Station()`, by
    passing in the name of a station found in `Stations()`.
* `Schedule`
  * Construct via `bbcradio.Schedule()`, passing in a `Station()` and a
    date as a string in the "YYYY-MM-DD" format.
* `Programme`
  * Used to store details for a programme; a `Schedule()` contains a
    list of `Programme()`

See the [CLI client](bbcradio/cli.py) for an example.

## CLI client

After installing the package, run with `bbcradio_cli`:

```sh
bbcradio_cli -h                              # show help
bbcradio_cli stations                        # list stations
bbcradio_cli schedule "BBC Radio 1" "2020-01-27"  # display schedule
```

## Testing

Run the unit tests (using fixture HTML files, no network required):

```sh
uv run python -m pytest tests/test_api.py
```

Run the functional tests against the live BBC site (network required):

```sh
uv run python -m pytest tests/test_functional.py
```

Or run all tests:

```sh
make test
```
