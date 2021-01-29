import pathlib
import unittest
from collections import OrderedDict

import bbcradio
from lxml import html


class TestStations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = pathlib.Path("tests") / "fixtures" / "stations.html"
        with open(path, "r") as f:
            page_element = html.fromstring(f.read())

        cls.urls = bbcradio.Stations._extract(page_element)

    def test_correct_extracted_links(self):
        # NB: these links are relative as it is the get_htmlelement() helper
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

    def test_correct_select(self):
        stations = bbcradio.Stations(self.urls)
        station = stations.select("BBC Radio 1")
        self.assertEqual(
            bbcradio.Station("BBC Radio 1", "/schedules/p00fzl86"), station
        )

    def test_incorrect_select(self):
        stations = bbcradio.Stations(self.urls)
        self.assertRaises(
            bbcradio.InvalidStationError,
            stations.select,
            "BBC Radio Not Present",
        )


class TestSchedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = pathlib.Path("tests") / "fixtures" / "schedule.html"
        with open(path, "r") as f:
            page_element = html.fromstring(f.read())

        cls.programmes = bbcradio.Schedule._extract(page_element)

    def test_construct_url(self):
        station = bbcradio.Station(
            "BBC Unittest Station", "https://example.com/unittest"
        )
        test_date = "2021-01-24"
        schedule = bbcradio.Schedule(station, test_date)
        self.assertEqual(
            "https://example.com/unittest/2021/01/24",
            schedule._construct_url(),
        )

    def test_correct_extracted_programmes(self):
        self.maxDiff = None
        expected_programmes = [
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T00:00:00+00:00",
                    "series_name": "Radio 1's Essential Mix",
                    "name": "Vintage Culture",
                    "description": "The Brazilian superstar DJ takes control of the Essential Mix decks.",
                    "identifier": "m000rcdj",
                    "url": "https://www.bbc.co.uk/programmes/m000rcdj",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T02:00:00+00:00",
                    "series_name": "Radio 1 Dance Presents...",
                    "name": "DJ Mag: Nightwave",
                    "description": "DJ Mag takes us to Scotland for an hour of bass, techno and blistering acid with Nightwave",
                    "identifier": "m000rcdn",
                    "url": "https://www.bbc.co.uk/programmes/m000rcdn",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T03:00:00+00:00",
                    "series_name": "Annie Mac in the Mix",
                    "name": "Piano House!",
                    "description": "Annie celebrates all things Piano house, old and new!",
                    "identifier": "m000rcds",
                    "url": "https://www.bbc.co.uk/programmes/m000rcds",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T03:30:00+00:00",
                    "series_name": "Annie Mac in the Mix",
                    "name": "House and Disco!",
                    "description": "Annie serves up another special mix.",
                    "identifier": "m000q2lm",
                    "url": "https://www.bbc.co.uk/programmes/m000q2lm",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T04:00:00+00:00",
                    "series_name": "Radio 1's Wind Down Presents...",
                    "name": "Intergral Records: Phil.Osophy",
                    "description": "Music designed to unwind the mind.",
                    "identifier": "m000rcdx",
                    "url": "https://www.bbc.co.uk/programmes/m000rcdx",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T05:00:00+00:00",
                    "series_name": "The Happy Hour from Radio 1",
                    "name": "Feel Good Happy Tunes!",
                    "description": "Feel good and happy tunes that will keep you smiling during lockdown life!",
                    "identifier": "m000rdqj",
                    "url": "https://www.bbc.co.uk/programmes/m000rdqj",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T06:00:00+00:00",
                    "series_name": "Radio 1 Dance",
                    "name": "24/7 Dance...",
                    "description": "Classic hits and the best new dance tracks.",
                    "identifier": "m000rl69",
                    "url": "https://www.bbc.co.uk/programmes/m000rl69",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T07:00:00+00:00",
                    "series_name": "Adele Roberts",
                    "name": "23/01/2021",
                    "description": "Adele Roberts takes charge of your weekend wake-up...",
                    "identifier": "m000rl6c",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6c",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T10:00:00+00:00",
                    "series_name": "Radio 1 Anthems",
                    "name": "with Adele Roberts",
                    "description": "Big anthems and tunes you haven't heard in ages!",
                    "identifier": "m000rl6f",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6f",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T10:32:00+00:00",
                    "series_name": "Radio 1 Anthems",
                    "name": "with Jordan North",
                    "description": "Big anthems and tunes you haven't heard in ages!",
                    "identifier": "m000rl6h",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6h",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T11:00:00+00:00",
                    "series_name": "Jordan North",
                    "name": "23/01/2021",
                    "description": "Big hits and the best new music.",
                    "identifier": "m000rl6k",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6k",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T13:00:00+00:00",
                    "series_name": "Matt and Mollie",
                    "name": "23/01/2021",
                    "description": "Afternoon fun and games with Matt Edmondson and Mollie King",
                    "identifier": "m000rl6m",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6m",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T16:00:00+00:00",
                    "series_name": "Radio 1's Dance Anthems",
                    "name": "Classic Dance Anthems with Charlie Hedges",
                    "description": "Charlie crosses the spectrum of Dance music with tracks from Mella Dee, Otto Knows & Mylo.",
                    "identifier": "m000rl6p",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6p",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T17:00:00+00:00",
                    "series_name": "Radio 1's Dance Anthems",
                    "name": "Classic Dance Anthems with Charlie Hedges",
                    "description": "Charlie continues the party with anthems from Patrick Topping, Weiss and The Prodigy.",
                    "identifier": "m000rl6r",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6r",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T18:00:00+00:00",
                    "series_name": "Radio 1's Dance Anthems",
                    "name": "Today's Dance Anthems with Charlie Hedges",
                    "description": "Charlie mixes up the biggest Dance Anthems.",
                    "identifier": "m000rl6t",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6t",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T19:00:00+00:00",
                    "series_name": "1Xtra's Takeover with DJ Target",
                    "name": "Kenny sits in for Target with a 50 Cent Versus Mix",
                    "description": "Kenny Allstar is in for Target as 1Xtra takes over Radio 1!",
                    "identifier": "m000rl6w",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6w",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T21:00:00+00:00",
                    "series_name": "1Xtra's Rap Show with Tiffany Calver",
                    "name": "Fredo Street Heat",
                    "description": "All the latest hits and heat from the world of Rap plus Fredo is this weeks street heat.",
                    "identifier": "m000rl6y",
                    "url": "https://www.bbc.co.uk/programmes/m000rl6y",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-23T23:00:00+00:00",
                    "series_name": "Diplo and Friends",
                    "name": "Diplo in the Mix",
                    "description": "Diplo in the mix exclusively for Diplo and friends - only on Radio 1 and 1Xtra.",
                    "identifier": "m000rl70",
                    "url": "https://www.bbc.co.uk/programmes/m000rl70",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-24T01:00:00+00:00",
                    "series_name": "Radio 1's Classic Essential Mix",
                    "name": "Four Tet 2010",
                    "description": "Relive Four Tet's Essential Mix debut from 2010.",
                    "identifier": "m000rl74",
                    "url": "https://www.bbc.co.uk/programmes/m000rl74",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-24T03:00:00+00:00",
                    "series_name": "Danny Howard's Club Mix",
                    "name": "Episode 2",
                    "description": "Danny goes in with a another Feel Good Club Mix.",
                    "identifier": "m000rl76",
                    "url": "https://www.bbc.co.uk/programmes/m000rl76",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-24T04:00:00+00:00",
                    "series_name": "Radio 1's Dance Anthems",
                    "name": "Classic Dance Anthems with Charlie Hedges",
                    "description": "Non-stop Classic Dance Anthems with Charlie!",
                    "identifier": "m000rl78",
                    "url": "https://www.bbc.co.uk/programmes/m000rl78",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2021-01-24T05:00:00+00:00",
                    "series_name": "Radio 1's Wind Down Presents...",
                    "name": "Integral: Emma G & MC Tali",
                    "description": "Integral's Emma G & MC Tali provide the Wind Down Mix.",
                    "identifier": "m000qkz2",
                    "url": "https://www.bbc.co.uk/programmes/m000qkz2",
                }
            ),
        ]

        self.assertEqual(expected_programmes, self.programmes)

    def test_create_with_valid_date(self):
        station = bbcradio.Station(
            "BBC Unittest Station", "https://example.com/unittest"
        )
        test_date = "2021-01-24"
        schedule = bbcradio.Schedule(station, test_date)
        self.assertEqual("BBC Unittest Station", schedule.station.name)
        self.assertEqual("https://example.com/unittest", schedule.station.url)
        self.assertIsNone(schedule._programmes)  # Avoid really computing.
        self.assertEqual(test_date, schedule.date)

    def test_create_with_invalid_date(self):
        station = bbcradio.Station(
            "BBC Unittest Station", "https://example.com/unittest"
        )
        self.assertRaises(
            bbcradio.InvalidDateError, bbcradio.Schedule, station, "not-a-date"
        )


class TestProgramme(unittest.TestCase):
    def test_create_with_all_valid_values(self):
        info = {
            "start_date": "2021-01-24T05:00:00+00:00",
            "series_name": "Radio 1's Wind Down Presents...",
            "name": "Integral: Emma G & MC Tali",
            "description": "Integral's Emma G & MC Tali provide the Wind Down Mix.",
            "identifier": "m000qkz2",
            "url": "https://www.bbc.co.uk/programmes/m000qkz2",
        }
        programme = bbcradio.Programme(**info)

        expected_programme = bbcradio.Programme()
        expected_programme._info = info

        self.assertEqual(expected_programme, programme)

    def test_create_with_some_invalid_values(self):
        original_info = {
            "start_date": "2021-01-24T05:00:00+00:00",
            "series_name": "Radio 1's Wind Down Presents...",
            "name": "Integral: Emma G & MC Tali",
            "description": "Integral's Emma G & MC Tali provide the Wind Down Mix.",
            "identifier": "m000qkz2",
            "url": "https://www.bbc.co.uk/programmes/m000qkz2",
        }
        info = original_info.copy()
        info["nonhandled_info"] = "Some unnecessary information"
        programme = bbcradio.Programme(**info)

        expected_programme = bbcradio.Programme()
        expected_programme._info = original_info

        self.assertEqual(expected_programme, programme)
