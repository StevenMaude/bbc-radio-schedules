# bbc-radio-schedules :radio::spiral_notepad:

Implements an unofficial API client in Python and provides an example
command-line client for processing BBC Radio station programme
schedules.

## Install

Install with `pip` or `poetry`, e.g.

```
pip install git+https://github.com/StevenMaude/bbc-radio-schedules
```

(or use `pip install git+git`… in the command above).

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
> bbcradio_cli -h # show help
> bbcradio_cli stations # list stations
> bbcradio_cli schedule "BBC Radio 1" "2020-01-27" # display schedule
```
