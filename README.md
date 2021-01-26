# bbc-radio-schedules

Implements an unofficial API client and provides an example command-line
client for processing BBC Radio station programme schedules.

Code licensed under the [MIT License](LICENSE).

## Summary of API client

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

## Design notes and thoughts

### Research

* Spent about an hour's research looking around the BBC Sounds site:
  * Looked at site pages with browser developer tools and downloaded
    pages with `cURL --compressed` (they're gzipped).
  * The schedules don't seem to have a machine-readable format. 
  * Schedules for a given station on a given day are in the HTML as a
    Schema JSON object in a `<script>` element.
  * Could load this JSON straight into `jq` by just selecting the
    correct line with `sed`.
* There is an internal BBC API that you can spot with developer tools,
  but it is marked "for internal use only". So will build on just what
  is available via simple HTTP requests to the main
  `https://www.bbc.co.uk` site as this is much more representative of an
  actual user-facing web client.

### Requirements

#### Must
 
* Display BBC radio schedules in Linux terminal.
* Provide a basic API client.
* Implement a basic command-line client on that API client.
* Specify a station to display.

#### Should

* Run with currently supported Python (3.6 and up).
* Have tests.
* Specify a date to allow other than today to be retrieved.

#### Could

* Get the tracklisting of a particular programme.
* Have pretty output; `rich` python package? Are there others?
* Integrate into `get_iplayer`; select programme ID from a schedule?
* Try mypy again?

### Shape of site

#### Schedules page

There is a [schedules page](https://www.bbc.co.uk/sounds/schedules).

This lists all radio stations available on it. These contain links.

Doesn't appear to be any other way to access the list of stations. This
will need querying, but is pretty simple.

#### Radio station page

```python
requests.get("https://www.bbc.co.uk/schedules/p00fzl86/YYYY/MM/DD")
```

This page has a schema JSON object we can extract directly.

#### From notes on a previous tool I made

You can access tracklistings directly, see [this
comment](https://github.com/StevenMaude/bbc-radio-tracklisting-downloader/issues/31#issuecomment-500241711).
