import pathlib
import unittest
from collections import OrderedDict

import bbcradio
from lxml import html


class TestRetrieveStations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = pathlib.Path("fixtures") / "stations.html"
        with open(path, "r") as f:
            page_element = html.fromstring(f.read())

        cls.urls = bbcradio.Stations._retrieve(page_element)

    def test_extracted_station_links(self):
        # NB: these links are relative as it is the request_url() helper
        # that makes links absolute.
        expected_urls = OrderedDict(
            [
                ("BBC Radio 1", "/schedules/p00fzl86"),
                ("BBC Radio 1Xtra", "/schedules/p00fzl64"),
                ("BBC Radio 2", "/schedules/p00fzl8v"),
                ("BBC Radio 3", "/schedules/p00fzl8t"),
                ("BBC Radio 4", "/schedules/p00fzl7j"),
                ("BBC Radio 4 Extra", "/schedules/p00fzl7l"),
                ("BBC Radio 5 live", "/schedules/p00fzl7g"),
                ("BBC Radio 5 live sports extra", "/schedules/p00fzl7h"),
                ("BBC Radio 6 Music", "/schedules/p00fzl65"),
                ("BBC Asian Network", "/schedules/p00fzl68"),
                ("BBC World Service", "/schedules/p00fzl9p"),
                ("BBC Radio Scotland", "/schedules/p00fzl8d"),
                ("BBC Radio nan Gàidheal", "/schedules/p00fzl81"),
                ("BBC Radio Ulster", "/schedules/p00fzl8w"),
                ("BBC Radio Foyle", "/schedules/p00fzl7m"),
                ("BBC Radio Wales", "/schedules/p00fzl8y"),
                ("BBC Radio Cymru", "/schedules/p00fzl7b"),
                ("BBC Radio Berkshire", "/schedules/p00fzl74"),
                ("BBC Radio Bristol", "/schedules/p00fzl75"),
                ("BBC Radio Cambridgeshire", "/schedules/p00fzl76"),
                ("BBC Radio Cornwall", "/schedules/p00fzl77"),
                ("BBC Coventry & Warwickshire", "/schedules/p00fzl78"),
                ("BBC Radio Cumbria", "/schedules/p00fzl79"),
                ("BBC Radio Derby", "/schedules/p00fzl7c"),
                ("BBC Radio Devon", "/schedules/p00fzl7d"),
                ("BBC Essex", "/schedules/p00fzl7f"),
                ("BBC Radio Gloucestershire", "/schedules/p00fzl7n"),
                ("BBC Radio Guernsey", "/schedules/p00fzl7p"),
                ("BBC Hereford & Worcester", "/schedules/p00fzl7q"),
                ("BBC Radio Humberside", "/schedules/p00fzl7r"),
                ("BBC Radio Jersey", "/schedules/p00fzl7s"),
                ("BBC Radio Kent", "/schedules/p00fzl7t"),
                ("BBC Radio Lancashire", "/schedules/p00fzl7v"),
                ("BBC Radio Leeds", "/schedules/p00fzl7w"),
                ("BBC Radio Leicester", "/schedules/p00fzl7x"),
                ("BBC Radio Lincolnshire", "/schedules/p00fzl7y"),
                ("BBC Radio London", "/schedules/p00fzl6f"),
                ("BBC Radio Manchester", "/schedules/p00fzl7z"),
                ("BBC Radio Merseyside", "/schedules/p00fzl80"),
                ("BBC Newcastle", "/schedules/p00fzl82"),
                ("BBC Radio Norfolk", "/schedules/p00fzl83"),
                ("BBC Radio Northampton", "/schedules/p00fzl84"),
                ("BBC Radio Nottingham", "/schedules/p00fzl85"),
                ("BBC Radio Oxford", "/schedules/p00fzl8c"),
                ("BBC Radio Sheffield", "/schedules/p00fzl8h"),
                ("BBC Radio Shropshire", "/schedules/p00fzl8k"),
                ("BBC Radio Solent", "/schedules/p00fzl8l"),
                ("BBC Somerset", "/schedules/p00fzl8m"),
                ("BBC Radio Stoke", "/schedules/p00fzl8n"),
                ("BBC Radio Suffolk", "/schedules/p00fzl8p"),
                ("BBC Surrey", "/schedules/p00fzl8q"),
                ("BBC Sussex", "/schedules/p00fzl8r"),
                ("BBC Tees", "/schedules/p00fzl93"),
                ("BBC Three Counties Radio", "/schedules/p00fzl96"),
                ("BBC Wiltshire", "/schedules/p00fzl8z"),
                ("BBC WM 95.6", "/schedules/p00fzl9f"),
                ("BBC Radio York", "/schedules/p00fzl90"),
            ]
        )
        self.assertEqual(expected_urls, self.urls)
