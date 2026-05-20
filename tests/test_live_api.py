import datetime as dt
import unittest

import bbcradio


class TestLiveBBCSite(unittest.TestCase):
    def test_can_fetch_live_station_schedule(self):
        stations = bbcradio.Stations()
        self.assertIn("BBC Radio 2", stations.urls)

        today = dt.datetime.now(dt.UTC).date().isoformat()
        schedule = bbcradio.Schedule(stations.select("BBC Radio 2"), today)
        programmes = schedule.programmes

        self.assertGreater(len(programmes), 0)

        first_programme = programmes[0].info
        self.assertIsNotNone(first_programme["start_date"])
        self.assertTrue(
            first_programme["series_name"] or first_programme["name"]
        )
        self.assertIsNotNone(first_programme["identifier"])
        self.assertTrue(
            str(first_programme["url"]).startswith(
                "https://www.bbc.co.uk/programmes/"
            )
        )
