import pathlib
import unittest

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
        expected_urls = {
            "Radio 1": "/sounds/schedules/bbc_radio_one",
            "Radio 1 Anthems": "/sounds/schedules/bbc_radio_one_anthems",
            "Radio 1 Dance": "/sounds/schedules/bbc_radio_one_dance",
            "Radio 1Xtra": "/sounds/schedules/bbc_1xtra",
            "Radio 2": "/sounds/schedules/bbc_radio_two",
            "Radio 3": "/sounds/schedules/bbc_radio_three",
            "Radio 3 Unwind": "/sounds/schedules/bbc_radio_three_unwind",
            "Radio 4": "/sounds/schedules/bbc_radio_fourfm",
            "Radio 4 Extra": "/sounds/schedules/bbc_radio_four_extra",
            "Radio 5 Live": "/sounds/schedules/bbc_radio_five_live",
            "Radio 5 Sports Extra": "/sounds/schedules/bbc_radio_five_live_sports_extra",
            "Radio 5 Sports Extra 2": "/sounds/schedules/bbc_radio_five_sports_extra_2",
            "Radio 5 Sports Extra 3": "/sounds/schedules/bbc_radio_five_sports_extra_3",
            "Radio 6 Music": "/sounds/schedules/bbc_6music",
            "Asian Network": "/sounds/schedules/bbc_asian_network",
            "World Service": "/sounds/schedules/bbc_world_service",
            "Live News": "/sounds/schedules/bbc_sounds_news",
            "Radio Scotland": "/sounds/schedules/bbc_radio_scotland_fm",
            "Radio Scotland Extra": "/sounds/schedules/bbc_radio_scotland_mw",
            "Radio Orkney": "/sounds/schedules/bbc_radio_orkney",
            "Radio Shetland": "/sounds/schedules/bbc_radio_shetland",
            "Radio nan Gàidheal": "/sounds/schedules/bbc_radio_nan_gaidheal",
            "Radio Ulster": "/sounds/schedules/bbc_radio_ulster",
            "Radio Foyle": "/sounds/schedules/bbc_radio_foyle",
            "Radio Wales": "/sounds/schedules/bbc_radio_wales_fm",
            "Radio Wales Extra": "/sounds/schedules/bbc_radio_wales_am",
            "Radio Cymru": "/sounds/schedules/bbc_radio_cymru",
            "Radio Cymru 2": "/sounds/schedules/bbc_radio_cymru_2",
            "CBeebies Radio": "/sounds/schedules/cbeebies_radio",
            "BBC Radio Berkshire": "/sounds/schedules/bbc_radio_berkshire",
            "BBC Radio Bristol": "/sounds/schedules/bbc_radio_bristol",
            "BBC Radio Cambridgeshire": "/sounds/schedules/bbc_radio_cambridge",
            "BBC Radio Cornwall": "/sounds/schedules/bbc_radio_cornwall",
            "BBC CWR": "/sounds/schedules/bbc_radio_coventry_warwickshire",
            "BBC Radio Cumbria": "/sounds/schedules/bbc_radio_cumbria",
            "BBC Radio Derby": "/sounds/schedules/bbc_radio_derby",
            "BBC Radio Devon": "/sounds/schedules/bbc_radio_devon",
            "BBC Essex": "/sounds/schedules/bbc_radio_essex",
            "BBC Radio Gloucestershire": "/sounds/schedules/bbc_radio_gloucestershire",
            "BBC Radio Guernsey": "/sounds/schedules/bbc_radio_guernsey",
            "BBC Hereford & Worcester": "/sounds/schedules/bbc_radio_hereford_worcester",
            "BBC Radio Humberside": "/sounds/schedules/bbc_radio_humberside",
            "BBC Radio Jersey": "/sounds/schedules/bbc_radio_jersey",
            "BBC Radio Kent": "/sounds/schedules/bbc_radio_kent",
            "BBC Radio Lancashire": "/sounds/schedules/bbc_radio_lancashire",
            "BBC Radio Leeds": "/sounds/schedules/bbc_radio_leeds",
            "BBC Radio Leicester": "/sounds/schedules/bbc_radio_leicester",
            "BBC Radio Lincolnshire": "/sounds/schedules/bbc_radio_lincolnshire",
            "BBC Radio London": "/sounds/schedules/bbc_london",
            "BBC Radio Manchester": "/sounds/schedules/bbc_radio_manchester",
            "BBC Radio Merseyside": "/sounds/schedules/bbc_radio_merseyside",
            "BBC Radio Newcastle": "/sounds/schedules/bbc_radio_newcastle",
            "BBC Radio Norfolk": "/sounds/schedules/bbc_radio_norfolk",
            "BBC Radio Northampton": "/sounds/schedules/bbc_radio_northampton",
            "BBC Radio Nottingham": "/sounds/schedules/bbc_radio_nottingham",
            "BBC Radio Oxford": "/sounds/schedules/bbc_radio_oxford",
            "BBC Radio Sheffield": "/sounds/schedules/bbc_radio_sheffield",
            "BBC Radio Shropshire": "/sounds/schedules/bbc_radio_shropshire",
            "BBC Radio Solent": "/sounds/schedules/bbc_radio_solent",
            "BBC Radio Solent Dorset": "/sounds/schedules/bbc_radio_solent_west_dorset",
            "BBC Radio Somerset": "/sounds/schedules/bbc_radio_somerset_sound",
            "BBC Radio Stoke": "/sounds/schedules/bbc_radio_stoke",
            "BBC Radio Suffolk": "/sounds/schedules/bbc_radio_suffolk",
            "BBC Radio Surrey": "/sounds/schedules/bbc_radio_surrey",
            "BBC Radio Sussex": "/sounds/schedules/bbc_radio_sussex",
            "BBC Radio Tees": "/sounds/schedules/bbc_tees",
            "BBC Three Counties Radio": "/sounds/schedules/bbc_three_counties_radio",
            "BBC Radio Wiltshire": "/sounds/schedules/bbc_radio_wiltshire",
            "BBC Radio WM": "/sounds/schedules/bbc_wm",
            "BBC Radio York": "/sounds/schedules/bbc_radio_york",
        }
        self.assertEqual(expected_urls, self.urls)

    def test_correct_select(self):
        stations = bbcradio.Stations(self.urls)
        station = stations.select("Radio 1")
        self.assertEqual(
            bbcradio.Station("Radio 1", "/sounds/schedules/bbc_radio_one"),
            station,
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
        test_date = "2026-05-19"
        schedule = bbcradio.Schedule(station, test_date)
        self.assertEqual(
            "https://example.com/unittest/2026-05-19",
            schedule._construct_url(),
        )

    def test_correct_extracted_programmes(self):
        self.maxDiff = None
        expected_programmes = [
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-18T22:00:00Z",
                    "series_name": "Radio 1's Rock Show with Daniel P Carter",
                    "name": "Alyx Holcombe sits in: Certified Baddiecore",
                    "description": (
                        "Get ready to enter your baddiecore era as Alyx"
                        " celebrates the rise of the movement redefining heavy"
                        " music, with huge tracks from Sleep Token, Bad Omens,"
                        " Poppy and more!\n\nProduced by Listen for BBC Radio 1."
                    ),
                    "identifier": "m002w7ql",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w7ql",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T00:00:00Z",
                    "series_name": "BBC Introducing Rock on Radio 1",
                    "name": "with Alyx Holcombe: Saint Agnes Track of the Week",
                    "description": (
                        "Alyx has a brand new Track of the Week from Saint Agnes,"
                        " plus a Mosh Pit selection featuring emerging artists"
                        " from the North East, plus tracks from Silo, HENKA,"
                        " Cober Mouth, Ded Pets & more.\n\nProduced by BBC Audio"
                        " for BBC Radio 1."
                    ),
                    "identifier": "m002w7qq",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w7qq",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T01:00:00Z",
                    "series_name": "Radio 1 Anthems",
                    "name": "Robyn, Coldplay, Example and more",
                    "description": (
                        "Alice Hopkins with big anthems and tunes you haven't"
                        " heard in ages.\n\nProduced in Glasgow by BBC Audio for"
                        " BBC Radio 1 Anthems."
                    ),
                    "identifier": "m002r550",
                    "url": "https://www.bbc.co.uk/sounds/play/m002r550",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T03:00:00Z",
                    "series_name": "Radio 1 Pop Anthems",
                    "name": "Ariana Grande, Doja Cat, Lizzo and more",
                    "description": (
                        "Nonstop singalong pop with Dean McCullough!\n\nProduced"
                        " in Salford by BBC Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w7qv",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w7qv",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T04:00:00Z",
                    "series_name": "Radio 1 Early Breakfast",
                    "name": "with Dean McCullough",
                    "description": (
                        "Dean McCullough has Radio 1's Early Breakfast.\n\nProduced"
                        " in Salford by BBC Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w7qx",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w7qx",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T05:58:00Z",
                    "series_name": "Radio 1 Newsbeat",
                    "name": "19/05/2026",
                    "description": (
                        "The latest news from around the UK and around the world."
                    ),
                    "identifier": "m002w6d7",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6d7",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T06:00:00Z",
                    "series_name": "Radio 1 Breakfast with Greg James",
                    "name": "Greg is LIVE in Sunderland!",
                    "description": (
                        "Greg is in Sunderland giving you a chance to get your"
                        " hands on some Big Weekend tickets!\n\nProduced by BBC"
                        " Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6d9",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6d9",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T09:30:00Z",
                    "series_name": "Radio 1 Newsbeat",
                    "name": "19/05/2026",
                    "description": (
                        "The latest news from around the UK and around the world."
                    ),
                    "identifier": "m002w6dc",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dc",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T09:33:00Z",
                    "series_name": "Rickie, Melvin and Charlie",
                    "name": "Mess with Melvin",
                    "description": (
                        "Rickie and Charlie try and confuse Melvin with their"
                        " strange facts from around the world.\n\nProduced by BBC"
                        " Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6df",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6df",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T11:45:00Z",
                    "series_name": "Newsbeat",
                    "name": "Guardiola to go",
                    "description": (
                        "Newsbeat's hearing your reaction as Pep Guardiola looks"
                        " set to stand down as the Manchester City boss this"
                        " weekend, with Enzo Maresca being lined up as his"
                        " replacement.\n\nProduced in Birmingham by BBC News for"
                        " BBC Radio 1, BBC Radio 1Xtra and BBC Asian Network."
                    ),
                    "identifier": "m002w6dh",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dh",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T12:00:00Z",
                    "series_name": "Matt and Mollie",
                    "name": "Matt v Mollie",
                    "description": (
                        "Things are about to get heated in another round of Matt"
                        " v Mollie!\n\nProduced by BBC Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6dk",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dk",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T14:30:00Z",
                    "series_name": "Radio 1 Newsbeat",
                    "name": "19/05/2026",
                    "description": (
                        "The latest news from around the UK and around the world."
                    ),
                    "identifier": "m002w6dm",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dm",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T14:33:00Z",
                    "series_name": "Going Home with Vick, Katie and Jamie on Radio 1",
                    "name": "Can you complete the hardest quiz on the radio?",
                    "description": (
                        "We bring you the hardest quiz on the radio, Complete"
                        " the Year.\n\nProduced by BBC Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6dp",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dp",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T16:45:00Z",
                    "series_name": "Newsbeat",
                    "name": "Scotland's World Cup squad",
                    "description": (
                        "19-year-old Rangers winger Findlay Curtis makes the cut,"
                        " along with the likes of Ross Stewart and Scott McTominay,"
                        " as Scotland head to their first World Cup in 28"
                        " years.\n\nProduced in Birmingham by BBC News for BBC"
                        " Radio 1, BBC Radio 1Xtra and BBC Asian Network."
                    ),
                    "identifier": "m002w6dr",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dr",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T17:00:00Z",
                    "series_name": "BBC Radio 1's Big Weekend",
                    "name": "On Air",
                    "description": (
                        "Jack Saunders and Sian Eleri are in the North East with"
                        " a Hottest Record from Alessi Rose.\n\nProduced by BBC"
                        " Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6dt",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dt",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T19:00:00Z",
                    "series_name": "Radio 1's Future Artists with Sian Eleri",
                    "name": "Tara Kumar sits in",
                    "description": (
                        "Tara gets excited about Big Weekend, hearing from artists"
                        " playing this year's festival and rewinding Odeal's live"
                        " session from 2024.\n\nProduced by Listen for BBC Radio 1."
                    ),
                    "identifier": "m002w6dw",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dw",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T21:00:00Z",
                    "series_name": "Radio 1's Power Down Playlist with Sian Eleri",
                    "name": "Airplane Mode",
                    "description": (
                        "Songs for when you need to switch off the world, with"
                        " artists from Radio 1's Big Weekend 2026 line up,"
                        " including: Kehlani, Jorja Smith, Clementine Douglas"
                        " and more...\n\nProduced by BBC Audio for BBC Radio 1."
                    ),
                    "identifier": "m002w6dy",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6dy",
                }
            ),
            bbcradio.Programme(
                **{
                    "start_date": "2026-05-19T22:00:00Z",
                    "series_name": "Martha",
                    "name": "Nectax in the guest mix and Martha's Jorja Smith remixtape",
                    "description": (
                        "Join Martha for an exploration into underground electronic"
                        " music, featuring dubstep, garage, jungle, bass and so"
                        " much more.\n\nIn the Deep Frequencies mix, Martha"
                        " celebrates Jorja Smith's appearance at Radio 1's Big"
                        " Weekend in Sunderland with a remixtape full of edits"
                        " and flips of her tunes.\n\nNewcastle-based Nectax has"
                        " guest mix combining Chicago footwork and UK"
                        " jungle.\n\nProduced by We Are Grape for BBC Radio 1"
                        " Dance."
                    ),
                    "identifier": "m002w6f0",
                    "url": "https://www.bbc.co.uk/sounds/play/m002w6f0",
                }
            ),
        ]

        self.assertEqual(expected_programmes, self.programmes)

    def test_create_with_valid_date(self):
        station = bbcradio.Station(
            "BBC Unittest Station", "https://example.com/unittest"
        )
        test_date = "2026-05-19"
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
            bbcradio.InvalidDateError,
            bbcradio.Schedule,
            station,
            "not-a-date",
        )


class TestProgramme(unittest.TestCase):
    def test_create_with_all_valid_values(self):
        info = {
            "start_date": "2026-05-19T22:00:00Z",
            "series_name": "Martha",
            "name": "Nectax in the guest mix and Martha's Jorja Smith remixtape",
            "description": "Martha takes you on a journey.",
            "identifier": "m002w6f0",
            "url": "https://www.bbc.co.uk/sounds/play/m002w6f0",
        }
        programme = bbcradio.Programme(**info)

        expected_programme = bbcradio.Programme()
        expected_programme._info = info

        self.assertEqual(expected_programme, programme)

    def test_create_with_some_invalid_values(self):
        original_info = {
            "start_date": "2026-05-19T22:00:00Z",
            "series_name": "Martha",
            "name": "Nectax in the guest mix and Martha's Jorja Smith remixtape",
            "description": "Martha takes you on a journey.",
            "identifier": "m002w6f0",
            "url": "https://www.bbc.co.uk/sounds/play/m002w6f0",
        }
        info = original_info.copy()
        info["nonhandled_info"] = "Some unnecessary information"
        programme = bbcradio.Programme(**info)

        expected_programme = bbcradio.Programme()
        expected_programme._info = original_info

        self.assertEqual(expected_programme, programme)
