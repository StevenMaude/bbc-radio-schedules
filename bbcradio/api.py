# encoding: utf-8
"""
bbcradio.py: Unofficial API client for the BBC Radio schedules.
"""
import copy
import datetime
import json
from collections import OrderedDict

import requests
from lxml import html


def get_htmlelement(url):
    """Given a URL, returns lxml.HtmlElement from HTML response.

    Helper with timeout for requests."""
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    element = html.fromstring(r.text)
    element.make_links_absolute("https://www.bbc.co.uk")
    return element


class InvalidStationError(Exception):
    pass


class Stations:
    """Represents stations that have available schedules.

    TODO: detail the attributes and methods.

    _urls: dict of station name to URL
    """

    _stations_url = "https://www.bbc.co.uk/sounds/schedules"

    def __init__(self, urls=None):
        self._urls = urls

    @property
    def urls(self):
        if self._urls is None:
            element = get_htmlelement(self._stations_url)
            self._urls = self._extract(element)
        return self._urls.copy()

    def select(self, name):
        """ Returns a Station with the given name, if available, or None. """
        url = self.urls.get(name)
        if url is None:
            raise InvalidStationError(name)
        return Station(name, url)

    @staticmethod
    def _extract(element):
        """
        Given lxml.HtmlElement, returns an OrderedDict of station name to URL.

        Take content from request.
        """
        urls = OrderedDict()

        national_xpath = "//img[@class='station-logo']"
        for elem in element.xpath(national_xpath):
            (station_name,) = elem.xpath("./@alt")
            (url,) = elem.xpath("../@href")
            urls[station_name] = url

        regional_xpath = "//div[@class='local-stations']//li/a"
        for elem in element.xpath(regional_xpath):
            (station_name,) = elem.xpath("./text()")
            (url,) = elem.xpath("./@href")
            urls[station_name] = url

        assert len(urls) > 0
        return urls

    def __repr__(self):
        return f"Stations(urls={repr(self._urls)})"

    def __eq__(self, other):
        return self._urls == other._urls


class Station:
    def __init__(self, name, url):
        self._name = name
        self._url = url

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    def __repr__(self):
        return f"Station(name={repr(self._name)}, url={repr(self._url)})"

    def __eq__(self, other):
        return self._name == other._name and self._url == other._url


class Schedule:
    def __init__(self, station, date):
        self._programmes = None
        self._station = station

        # Validate that this is a valid YYYY-MM-DD string.
        # Explicitly require a date, even though the station URL without a date
        # gives you the current day.
        datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # This date corresponds to the schedule date and may contain some
        # programmes outside of that date.
        self._date = date

    @property
    def programmes(self):
        if self._programmes is None:
            element = get_htmlelement(self._construct_url())
            self._programmes = self._extract(element)
        return copy.deepcopy(self._programmes)

    @property
    def station(self):
        return self._station

    @property
    def date(self):
        return self._date

    def _construct_url(self):
        return self._station.url + "/" + self._date.replace("-", "/")

    @staticmethod
    def _extract(element):
        schema_xpath = '//script[@type="application/ld+json"]/text()'
        schemas_text = element.xpath(schema_xpath)

        for schema_text in schemas_text:
            schedule_details = json.loads(schema_text)
            if schedule_details.get("@graph") is not None:
                break
            else:
                schedule_details = None

        assert schedule_details is not None

        programmes = []

        for programme_details in schedule_details["@graph"]:
            d = {}

            publication = programme_details.get("publication")
            if publication is not None:
                d["start_date"] = publication.get("startDate")

            series_details = programme_details.get("partOfSeries")
            if series_details is not None:
                d["series_name"] = series_details.get("name")

            d["name"] = programme_details.get("name")
            d["description"] = programme_details.get("description")
            d["identifier"] = programme_details.get("identifier")
            d["url"] = programme_details.get("url")

            programme = Programme(**d)
            programmes.append(programme)

        return programmes

    def __str__(self):
        return (
            "<Schedule "
            f"_station={repr(self._station)} _date={repr(self._date)}>"
        )

    def __eq__(self, other):
        return (
            self._programmes == other._programmes
            and self._station == other._station
            and self._date == other._date
        )


class Programme:
    def __init__(self, **kwargs):
        self._info = OrderedDict(
            [
                ("start_date", None),
                ("series_name", None),
                ("name", None),
                ("description", None),
                ("identifier", None),
                ("url", None),
            ],
        )

        for k in self._info:
            kwargs_value = kwargs.get(k)
            if kwargs_value is not None:
                self._info[k] = kwargs_value

    @property
    def info(self):
        return self._info.copy()

    def __repr__(self):
        return f"Programme({repr(dict(self._info))})"

    def __eq__(self, other):
        return self._info == other._info
