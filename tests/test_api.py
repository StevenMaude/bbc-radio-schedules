import pathlib
import unittest
from collections import OrderedDict

import bbcradio
from lxml import html

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


def load_fixture(name):
    return html.fromstring((FIXTURES_DIR / name).read_text())


class TestStations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.urls = bbcradio.Stations._extract(load_fixture("stations.html"))

    def test_correct_extracted_links(self):
        expected_urls = OrderedDict(
            [
                (
                    "BBC Radio 1",
                    "https://www.bbc.co.uk/sounds/schedules/bbc_radio_one",
                ),
                (
                    "BBC Radio 2",
                    "https://www.bbc.co.uk/sounds/schedules/bbc_radio_two",
                ),
                (
                    "BBC Essex",
                    "https://www.bbc.co.uk/sounds/schedules/bbc_radio_essex",
                ),
                (
                    "BBC CWR",
                    "https://www.bbc.co.uk/sounds/schedules/bbc_radio_coventry_warwickshire",
                ),
                (
                    "CBeebies Radio",
                    "https://www.bbc.co.uk/sounds/schedules/cbeebies_radio",
                ),
            ]
        )
        self.assertEqual(expected_urls, self.urls)

    def test_correct_select(self):
        stations = bbcradio.Stations(self.urls)
        station = stations.select("BBC Radio 1")
        self.assertEqual(
            bbcradio.Station(
                "BBC Radio 1",
                "https://www.bbc.co.uk/sounds/schedules/bbc_radio_one",
            ),
            station,
        )

    def test_select_supports_legacy_aliases(self):
        stations = bbcradio.Stations(self.urls)
        station = stations.select("bbc coventry & warwickshire")
        self.assertEqual(
            bbcradio.Station(
                "BBC CWR",
                "https://www.bbc.co.uk/sounds/schedules/bbc_radio_coventry_warwickshire",
            ),
            station,
        )

    def test_incorrect_select(self):
        stations = bbcradio.Stations(self.urls)
        with self.assertRaises(bbcradio.InvalidStationError):
            stations.select("BBC Radio Not Present")


class TestSchedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programmes = bbcradio.Schedule._extract(
            load_fixture("schedule.html")
        )

    def test_construct_url(self):
        station = bbcradio.Station(
            "BBC Unittest Station",
            "https://www.bbc.co.uk/sounds/schedules/unittest",
        )
        schedule = bbcradio.Schedule(station, "2021-01-24")
        self.assertEqual(
            "https://www.bbc.co.uk/sounds/schedules/unittest/2021-01-24",
            schedule._construct_url(),
        )

    def test_correct_extracted_programmes(self):
        expected_programmes = [
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T00:00:00Z",
                    "series_name": "Radio 1's Essential Mix",
                    "name": "Vintage Culture",
                    "description": "The Brazilian superstar DJ takes control of the Essential Mix decks.",
                    "identifier": "m000rcdj",
                    "url": "https://www.bbc.co.uk/programmes/m000rcdj",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T02:00:00Z",
                    "series_name": "Radio 1 Dance",
                    "name": "Radio 1 Dance",
                    "description": "Classic hits and the best new dance tracks.",
                    "identifier": "m000rl69",
                    "url": "https://www.bbc.co.uk/programmes/m000rl69",
                }
            ),
        ]
        self.assertEqual(expected_programmes, self.programmes)

    def test_create_with_valid_date(self):
        station = bbcradio.Station(
            "BBC Unittest Station",
            "https://www.bbc.co.uk/sounds/schedules/unittest",
        )
        schedule = bbcradio.Schedule(station, "2021-01-24")
        self.assertEqual("BBC Unittest Station", schedule.station.name)
        self.assertEqual(
            "https://www.bbc.co.uk/sounds/schedules/unittest",
            schedule.station.url,
        )
        self.assertIsNone(schedule._programmes)
        self.assertEqual("2021-01-24", schedule.date)

    def test_create_with_invalid_date(self):
        station = bbcradio.Station(
            "BBC Unittest Station",
            "https://www.bbc.co.uk/sounds/schedules/unittest",
        )
        with self.assertRaises(bbcradio.InvalidDateError):
            bbcradio.Schedule(station, "not-a-date")


class TestProgramme(unittest.TestCase):
    def test_create_with_all_valid_values(self):
        info = OrderedDict(
            [
                ("start_date", "2021-01-24T05:00:00+00:00"),
                ("series_name", "Radio 1's Wind Down Presents..."),
                ("name", "Integral: Emma G & MC Tali"),
                (
                    "description",
                    "Integral's Emma G & MC Tali provide the Wind Down Mix.",
                ),
                ("identifier", "m000qkz2"),
                ("url", "https://www.bbc.co.uk/programmes/m000qkz2"),
            ]
        )

        programme = bbcradio.Programme(**info)
        self.assertEqual(info, programme.info)

    def test_create_with_some_invalid_values(self):
        original_info = OrderedDict(
            [
                ("start_date", "2021-01-24T05:00:00+00:00"),
                ("series_name", "Radio 1's Wind Down Presents..."),
                ("name", "Integral: Emma G & MC Tali"),
                (
                    "description",
                    "Integral's Emma G & MC Tali provide the Wind Down Mix.",
                ),
                ("identifier", "m000qkz2"),
                ("url", "https://www.bbc.co.uk/programmes/m000qkz2"),
            ]
        )
        info = dict(original_info)
        info["nonhandled_info"] = "Some unnecessary information"

        programme = bbcradio.Programme(**info)
        self.assertEqual(original_info, programme.info)
