# encoding: utf-8

"""bbcradio.api
------------

This module implements an unofficial API to the BBC's radio station schedules.

Copyright (c) 2021 Steven Maude
Licensed under the MIT License, see LICENSE.
"""

import copy
import datetime
import json
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse

import requests
from lxml import html


class InvalidStationError(Exception):
    """Raised when an invalid station is selected from Stations."""

    pass


class InvalidDateError(Exception):
    """Raised if a supplied date is not YYYY-MM-DD format."""

    pass


class Stations:
    """Represents a collection of radio stations.

    Attributes:
        _stations_url: string, the stations URL.
    """

    _stations_url = "https://www.bbc.co.uk/sounds/schedules"

    def __init__(self, urls=None):
        """Inits Stations.

        Attributes:
            _urls: OrderedDict, mapping a station name as string to URL
            as string. Defaults to None. Set on first access of urls property.
        """
        self._urls = urls

    @property
    def urls(self):
        """Property getter for _urls; sets _urls on first access.

        Returns:
            OrderedDict, mapping a station name as string to URL as string.
            This is a shallow copy of _urls.
        """
        if self._urls is None:
            element = get_htmlelement(self._stations_url)
            self._urls = self._extract(element)
        return self._urls.copy()

    def select(self, name):
        """Returns a Station with the given name or raises an error.

        Arguments:
            name: string, the station name.

        Returns:
            Station.
        """
        url = self.urls.get(name)
        if url is None:
            raise InvalidStationError(name)
        return Station(name, url)

    @staticmethod
    def _extract(element):
        """Given lxml.HtmlElement, returns OrderedDict of station name to URL.

        Arguments:
            element: lxml.HtmlElement representing stations page.

        Returns:
            OrderedDict, station name as string to URL as string.

        Raises:
            AssertionError: No URLs are found.
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
    """Represents a single radio station."""

    def __init__(self, name, url):
        """Inits Station.

        Args:
            name: string, the station name.
            url: string, the station schedule URL.

        Attributes:
            _name: string, the station name.
            _url: string, the station schedule URL.
        """
        self._name = name
        self._url = url

    @property
    def name(self):
        """Property getter for _name."""
        return self._name

    @property
    def url(self):
        """Property getter for .url."""
        return self._url

    def __repr__(self):
        return f"Station(name={repr(self._name)}, url={repr(self._url)})"

    def __eq__(self, other):
        return self._name == other._name and self._url == other._url


class Schedule:
    """Represents a radio station schedule."""

    def __init__(self, station, date):
        """Inits Schedule.

        Arguments:
            station: Station.
            date: string, ISO8601 date in YYYY-MM-DD format.

        Attributes:
            _programmes: list of Programme; defaults to None. Set on first
                access of programmes property.
            _station: Station.
            date: string, ISO8601 date in YYYY-MM-DD format.

        Raises:
            ValueError: date provided was not in YYYY-MM-DD format.
        """
        self._programmes = None
        self._station = station

        # Validate that this is a valid YYYY-MM-DD string.
        # Explicitly require a date, even though the station URL without a date
        # gives you the current day.
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateError(f"invalid date: {date}")
        # This date corresponds to the schedule date and may contain some
        # programmes outside of that date.
        self._date = date

    @property
    def programmes(self):
        """Property getter for _programmes; sets _programmes on first access.

        Returns:
            list of Programme. This is a deep copy of _programmes.
        """
        if self._programmes is None:
            element = get_htmlelement(self._construct_url())
            self._programmes = self._extract(element)
        return copy.deepcopy(self._programmes)

    @property
    def station(self):
        """Property getter for _station.

        Returns:
            Station.
        """
        return self._station

    @property
    def date(self):
        """Property getter for _date.

        Returns:
            string, ISO8601 date in YYYY-MM-DD format.
        """
        return self._date

    def _construct_url(self):
        """Returns a full schedule URL including date.

        Returns:
            string, schedule URL including date.
        """
        return self._station.url + "/" + self._date.replace("-", "/")

    @staticmethod
    def _extract(element):
        """Returns a list of Programmes for a given schedule HTML page element.

        Arguments:
            element: lxml.HtmlElement of schedule page

        Returns:
            list of Programme.

        Raises:
            AssertionError: no schedule details found in element.
        """
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
    """Represents a radio programme."""

    def __init__(self, **kwargs):
        """Inits Programme.

        Arguments:
            **start_date: string, start date/time of programme.
            **series_name: string, series name of programme.
            **name: string, name of programme.
            **description: string, description of programme.
            **identifier: string, programme identifier.
            **url: string, URL of programme.

        Attributes:
            _info: OrderedDict, representing programme information. Constructed
                by **kwargs; see Arguments.
        """
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
        """Property getter for _info.

        Returns:
            OrderedDict representing programme information. This is a shallow
            copy of _info.
        """
        return self._info.copy()

    def __repr__(self):
        return f"Programme({repr(dict(self._info))})"

    def __eq__(self, other):
        return self._info == other._info


def get_htmlelement(url):
    """Fetches a URL and returns lxml.HtmlElement.

    Helper with timeout for requests.

    Args:
        url: string, the URL.

    Returns:
        lxml.HtmlElement representing the requested page.
    """
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    element = html.fromstring(r.text)

    parsed_url = urlparse(url)
    base_url = urlunparse(
        parsed_url._replace(path="", params="", query="", fragment="")
    )
    element.make_links_absolute(base_url)
    return element
