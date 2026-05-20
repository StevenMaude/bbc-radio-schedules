"""bbcradio.api
------------

This module implements an unofficial API to the BBC's radio station schedules.

Copyright (c) 2021 Steven Maude
Licensed under the MIT License, see LICENSE.
"""

import copy
import datetime
import json
from urllib.parse import urlparse, urlunparse

import requests
from lxml import html


class InvalidStationError(Exception):
    """Raised when an invalid station is selected from Stations."""


class InvalidDateError(Exception):
    """Raised if a supplied date is not YYYY-MM-DD format."""


class Stations:
    """Represents a collection of radio stations.

    Attributes:
        _stations_url: The stations listing URL.
    """

    _stations_url = "https://www.bbc.co.uk/sounds/schedules"

    def __init__(self, urls: dict[str, str] | None = None) -> None:
        """Inits Stations.

        Attributes:
            _urls: dict mapping a station name to URL.
                Defaults to None. Set on first access of urls property.
        """
        self._urls = urls

    @property
    def urls(self) -> dict[str, str]:
        """Property getter for _urls; sets _urls on first access.

        Returns:
            dict mapping a station name to URL. This is a shallow copy
            of _urls.
        """
        if self._urls is None:
            element = get_htmlelement(self._stations_url)
            self._urls = self._extract(element)
        return self._urls.copy()

    def select(self, name: str) -> "Station":
        """Returns a Station with the given name or raises an error.

        Arguments:
            name: The station name.

        Returns:
            Station.

        Raises:
            InvalidStationError: No station found with the given name.
        """
        url = self.urls.get(name)
        if url is None:
            raise InvalidStationError(name)
        return Station(name, url)

    @staticmethod
    def _extract(element: html.HtmlElement) -> dict[str, str]:
        """Given lxml.HtmlElement, returns dict of station name to URL.

        Arguments:
            element: lxml.HtmlElement representing stations page.

        Returns:
            dict, station name to URL.

        Raises:
            AssertionError: No URLs are found.
        """
        urls: dict[str, str] = {}

        # National stations: logo images inside anchor tags.
        national_xpath = "//img[@class='station-logo']"
        for elem in element.xpath(national_xpath):
            (station_name,) = elem.xpath("./@alt")
            (url,) = elem.xpath("../@href")
            urls[station_name] = url

        # Regional/local stations: plain text links inside a local-stations div.
        regional_xpath = "//div[@class='local-stations']//li/a"
        for elem in element.xpath(regional_xpath):
            (station_name,) = elem.xpath("./text()")
            (url,) = elem.xpath("./@href")
            urls[station_name] = url

        # Fallback: if neither selector found anything, try to scrape all
        # schedule links (href matching /schedules/<id>).  This handles
        # potential future redesigns of the BBC Sounds page.
        if not urls:
            fallback_xpath = "//a[contains(@href, '/schedules/')]"
            seen: set[str] = set()
            for elem in element.xpath(fallback_xpath):
                href = elem.get("href", "")
                if href in seen or not href:
                    continue
                seen.add(href)
                # Try to get a meaningful name from alt text of a child img, or
                # the link text itself.
                img_alts = elem.xpath(".//img/@alt")
                name = img_alts[0] if img_alts else elem.text_content().strip()
                if name:
                    urls[name] = href

        assert len(urls) > 0, "No station URLs found on the schedules page"
        return urls

    def __repr__(self) -> str:
        return f"Stations(urls={self._urls!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stations):
            return NotImplemented
        return self._urls == other._urls


class Station:
    """Represents a single radio station."""

    def __init__(self, name: str, url: str) -> None:
        """Inits Station.

        Args:
            name: The station name.
            url: The station schedule URL.
        """
        self._name = name
        self._url = url

    @property
    def name(self) -> str:
        """Property getter for _name."""
        return self._name

    @property
    def url(self) -> str:
        """Property getter for url."""
        return self._url

    def __repr__(self) -> str:
        return f"Station(name={self._name!r}, url={self._url!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Station):
            return NotImplemented
        return self._name == other._name and self._url == other._url


class Schedule:
    """Represents a radio station schedule."""

    def __init__(self, station: Station, date: str) -> None:
        """Inits Schedule.

        Arguments:
            station: Station.
            date: ISO 8601 date in YYYY-MM-DD format.

        Raises:
            InvalidDateError: date provided was not in YYYY-MM-DD format.
        """
        self._programmes: list["Programme"] | None = None
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
    def programmes(self) -> list["Programme"]:
        """Property getter for _programmes; sets _programmes on first access.

        Returns:
            list of Programme. This is a deep copy of _programmes.
        """
        if self._programmes is None:
            element = get_htmlelement(self._construct_url())
            self._programmes = self._extract(element)
        return copy.deepcopy(self._programmes)

    @property
    def station(self) -> Station:
        """Property getter for _station."""
        return self._station

    @property
    def date(self) -> str:
        """Property getter for _date."""
        return self._date

    def _construct_url(self) -> str:
        """Returns a full schedule URL including date.

        Returns:
            Schedule URL including date path segments.
        """
        return self._station.url + "/" + self._date.replace("-", "/")

    @staticmethod
    def _extract(element: html.HtmlElement) -> list["Programme"]:
        """Returns a list of Programmes for a given schedule HTML page element.

        Arguments:
            element: lxml.HtmlElement of schedule page.

        Returns:
            list of Programme.

        Raises:
            ValueError: no schedule details found in element.
        """
        schema_xpath = '//script[@type="application/ld+json"]/text()'
        schemas_text = element.xpath(schema_xpath)

        schedule_details: dict | None = None
        for schema_text in schemas_text:
            candidate = json.loads(schema_text)
            if candidate.get("@graph") is not None:
                schedule_details = candidate
                break

        if schedule_details is None:
            raise ValueError("schedule details not found in HTML element")

        programmes = []

        for programme_details in schedule_details["@graph"]:
            d: dict[str, str | None] = {}

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

    def __str__(self) -> str:
        return (
            "<Schedule "
            f"_station={self._station!r} _date={self._date!r}>"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Schedule):
            return NotImplemented
        return (
            self._programmes == other._programmes
            and self._station == other._station
            and self._date == other._date
        )


class Programme:
    """Represents a radio programme."""

    _FIELDS = ("start_date", "series_name", "name", "description", "identifier", "url")

    def __init__(self, **kwargs: str | None) -> None:
        """Inits Programme.

        Keyword Arguments:
            start_date: Start date/time of programme.
            series_name: Series name of programme.
            name: Name of programme.
            description: Description of programme.
            identifier: Programme identifier.
            url: URL of programme.
        """
        self._info: dict[str, str | None] = {field: None for field in self._FIELDS}

        for k in self._info:
            kwargs_value = kwargs.get(k)
            if kwargs_value is not None:
                self._info[k] = kwargs_value

    @property
    def info(self) -> dict[str, str | None]:
        """Property getter for _info.

        Returns:
            dict representing programme information. This is a shallow
            copy of _info.
        """
        return self._info.copy()

    def __repr__(self) -> str:
        return f"Programme({dict(self._info)!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Programme):
            return NotImplemented
        return self._info == other._info


def get_htmlelement(url: str) -> html.HtmlElement:
    """Fetches a URL and returns an lxml HtmlElement.

    Args:
        url: The URL to fetch.

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
