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

## Design notes and thoughts

### Requirements

#### Must
 
* Display BBC radio schedules in Linux terminal. :heavy_check_mark:
* Provide a basic API client. :heavy_check_mark:
* Implement a basic command-line client on that API client. :heavy_check_mark:
* Specify a station to display. :heavy_check_mark:

#### Should

* Run with currently supported Python (3.6 and up). :heavy_check_mark:
* Have tests. :heavy_check_mark:
* Specify a date to allow other than today to be retrieved. :heavy_check_mark:

#### Could

* Get the tracklisting of a particular programme.
  * You can access tracklistings directly, see [this comment](https://github.com/StevenMaude/bbc-radio-tracklisting-downloader/issues/31#issuecomment-500241711).
* Have pretty output; `rich` python package? Are there others?
* Integrate into `get_iplayer`; select programme ID from a schedule?
* Try mypy again?

