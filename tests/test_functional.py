"""Functional tests against the live BBC Sounds website.

These tests make real HTTP requests and will fail if the BBC website is
unavailable or if its HTML structure changes in a way that breaks parsing.

Run with:
    pytest tests/test_functional.py -v
or:
    python -m pytest tests/test_functional.py -v
"""

import datetime
import unittest

import bbcradio


class TestStationsFunctional(unittest.TestCase):
    """Functional tests for Stations against the live BBC site."""

    @classmethod
    def setUpClass(cls):
        cls.stations = bbcradio.Stations()

    def test_stations_returns_results(self):
        urls = self.stations.urls
        self.assertGreater(len(urls), 0)

    def test_known_national_station_present(self):
        urls = self.stations.urls
        self.assertIn("Radio 1", urls)

    def test_known_national_station_url_format(self):
        urls = self.stations.urls
        url = urls["Radio 1"]
        self.assertIn("/sounds/schedules/", url)

    def test_known_local_station_present(self):
        urls = self.stations.urls
        # A well-known local BBC station that should remain stable
        self.assertIn("BBC Radio Manchester", urls)

    def test_select_known_station(self):
        station = self.stations.select("Radio 1")
        self.assertEqual("Radio 1", station.name)
        self.assertIn("/sounds/schedules/", station.url)

    def test_select_unknown_station_raises(self):
        self.assertRaises(
            bbcradio.InvalidStationError,
            self.stations.select,
            "Not A Real Station",
        )


class TestScheduleFunctional(unittest.TestCase):
    """Functional tests for Schedule against the live BBC site."""

    @classmethod
    def setUpClass(cls):
        # Use a date two days ago to ensure the schedule is fully populated
        cls.test_date = (
            datetime.date.today() - datetime.timedelta(days=2)
        ).isoformat()
        stations = bbcradio.Stations()
        station = stations.select("Radio 1")
        cls.schedule = bbcradio.Schedule(station, cls.test_date)

    def test_schedule_has_programmes(self):
        programmes = self.schedule.programmes
        self.assertGreater(len(programmes), 0)

    def test_programmes_have_required_fields(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            info = programme.info
            # Every broadcast must have a start time and identifier
            self.assertIsNotNone(
                info["start_date"],
                f"Programme missing start_date: {programme}",
            )
            self.assertIsNotNone(
                info["identifier"],
                f"Programme missing identifier: {programme}",
            )
            self.assertIsNotNone(
                info["url"],
                f"Programme missing url: {programme}",
            )

    def test_programme_url_format(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            url = programme.info["url"]
            self.assertTrue(
                url.startswith("https://www.bbc.co.uk/sounds/play/"),
                f"Unexpected URL format: {url}",
            )

    def test_programme_start_date_format(self):
        programmes = self.schedule.programmes
        for programme in programmes:
            start = programme.info["start_date"]
            # Should be an ISO 8601 datetime string
            self.assertRegex(
                start,
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                f"Unexpected start_date format: {start}",
            )

    def test_schedule_station_and_date(self):
        self.assertEqual("Radio 1", self.schedule.station.name)
        self.assertEqual(self.test_date, self.schedule.date)
