import datetime as dt
import unittest

import requests

import bbcradio


class TestLiveBBCSite(unittest.TestCase):
    def test_live_station_schedule(self):
        stations = bbcradio.Stations()

        try:
            urls = stations.urls
        except requests.RequestException as exc:
            self.skipTest(f"live BBC site unavailable: {exc}")

        self.assertTrue(urls)

        station_name = next(
            (
                name
                for name in ("BBC Radio 4", "BBC Radio 2", "BBC Radio 1")
                if name in urls
            ),
            next(iter(urls)),
        )
        station = stations.select(station_name)
        schedule_date = (dt.date.today() - dt.timedelta(days=1)).isoformat()

        schedule = bbcradio.Schedule(station, schedule_date)
        programmes = schedule.programmes

        self.assertTrue(programmes)
        first_programme = programmes[0].info
        self.assertIsNotNone(first_programme["start_date"])
        self.assertTrue(first_programme["name"] or first_programme["url"])
