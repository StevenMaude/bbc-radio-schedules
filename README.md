# bbc-radio-schedules

Implements an unofficial API client and provides an example command-line
client for processing BBC Radio station programme schedules.

Code licensed under the [MIT License](LICENSE).

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

## CLI client

Run with `bbcradio_cli.py`:

```sh
> bbcradio_cli.py -h # show help
> bbcradio_cli.py stations # list stations
> bbcradio_cli.py schedule "BBC Radio 1" "2020-01-27" # display schedule
```
