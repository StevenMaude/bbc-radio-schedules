"""Functional tests that exercise the API against the live BBC website.

These tests are skipped when the BBC site is unreachable (e.g. in an
offline sandbox or a CI environment without outbound network access).
They are intended to catch regressions caused by changes to the BBC
Sounds website HTML structure or its JSON-LD schema.
"""

import datetime
import socket
import unittest

import bbcradio


def _bbc_reachable() -> bool:
    """Return True if www.bbc.co.uk can be resolved and connected to."""
    try:
        socket.setdefaulttimeout(5)
        socket.getaddrinfo("www.bbc.co.uk", 443)
        return True
    except OSError:
        return False


_SKIP_REASON = "www.bbc.co.uk is not reachable from this environment"


@unittest.skipUnless(_bbc_reachable(), _SKIP_REASON)
class TestLiveStations(unittest.TestCase):
    """Tests that verify the live stations listing page."""

    @classmethod
    def setUpClass(cls):
        cls.stations = bbcradio.Stations()

    def test_stations_returns_results(self):
        urls = self.stations.urls
        self.assertGreater(len(urls), 0, "Expected at least one station URL")

    def test_known_national_station_present(self):
        urls = self.stations.urls
        self.assertIn(
            "BBC Radio 1",
            urls,
            "BBC Radio 1 should be in the station list",
        )

    def test_station_urls_point_to_sounds_schedules(self):
        urls = self.stations.urls
        for name, url in urls.items():
            self.assertIn(
                "/schedules/",
                url,
                f"Station URL for {name!r} does not contain '/schedules/'",
            )

    def test_select_known_station(self):
        station = self.stations.select("BBC Radio 1")
        self.assertEqual("BBC Radio 1", station.name)
        self.assertIn("/schedules/", station.url)

    def test_select_invalid_station_raises(self):
        self.assertRaises(
            bbcradio.InvalidStationError,
            self.stations.select,
            "Not A Real Station XYZ",
        )


@unittest.skipUnless(_bbc_reachable(), _SKIP_REASON)
class TestLiveSchedule(unittest.TestCase):
    """Tests that verify live schedule retrieval for a known station."""

    # Use a historical date so the schedule content is fixed.
    _STATION_NAME = "BBC Radio 2"
    _DATE = "2021-01-30"

    @classmethod
    def setUpClass(cls):
        stations = bbcradio.Stations()
        station = stations.select(cls._STATION_NAME)
        cls.schedule = bbcradio.Schedule(station, cls._DATE)

    def test_schedule_station_name(self):
        self.assertEqual(self._STATION_NAME, self.schedule.station.name)

    def test_schedule_date(self):
        self.assertEqual(self._DATE, self.schedule.date)

    def test_schedule_has_programmes(self):
        programmes = self.schedule.programmes
        self.assertGreater(len(programmes), 0, "Expected at least one programme")

    def test_programme_fields_populated(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            info = programme.info
            # Every programme must have a name and a start_date.
            self.assertIsNotNone(
                info["name"],
                "Programme is missing a name",
            )
            self.assertIsNotNone(
                info["start_date"],
                f"Programme {info['name']!r} is missing a start_date",
            )

    def test_start_dates_are_iso8601(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            start_date = programme.info["start_date"]
            if start_date is None:
                continue
            # datetime.fromisoformat handles offset-aware strings in Py 3.11+
            try:
                datetime.datetime.fromisoformat(start_date)
            except ValueError:
                self.fail(
                    f"start_date {start_date!r} is not a valid ISO 8601 datetime"
                )

    def test_programme_urls_point_to_bbc(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            url = programme.info["url"]
            if url is None:
                continue
            self.assertTrue(
                url.startswith("https://www.bbc.co.uk/"),
                f"Programme URL {url!r} does not start with BBC domain",
            )
