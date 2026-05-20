# encoding: utf-8

"""Unofficial API for BBC radio station schedules."""

from __future__ import annotations

import copy
import datetime as dt
import json
from collections import OrderedDict
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from lxml import html

BBC_BASE_URL = "https://www.bbc.co.uk"
NEXT_DATA_XPATH = "//script[@id='__NEXT_DATA__']/text()"
REQUEST_HEADERS = {
    "User-Agent": (
        "bbcradio/0.2.0 "
        "(https://github.com/StevenMaude/bbc-radio-schedules)"
    )
}
STATION_NAME_OVERRIDES = {
    "bbc_radio_essex": "BBC Essex",
    "bbc_london": "BBC Radio London",
    "cbeebies_radio": "CBeebies Radio",
}
STATION_ALIASES = {
    "BBC Coventry & Warwickshire": "BBC CWR",
    "BBC Radio 5 live": "BBC Radio 5 Live",
    "BBC Radio 5 live sports extra": "BBC Radio 5 Sports Extra",
    "BBC Somerset": "BBC Radio Somerset",
    "BBC Tees": "BBC Radio Tees",
    "BBC WM": "BBC Radio WM",
    "BBC WM 95.6": "BBC Radio WM",
}


class InvalidStationError(ValueError):
    """Raised when an invalid station is selected from Stations."""


class InvalidDateError(ValueError):
    """Raised if a supplied date is not YYYY-MM-DD format."""


class Stations:
    """Represents a collection of radio stations."""

    _stations_url = f"{BBC_BASE_URL}/sounds/stations"

    def __init__(self, urls: OrderedDict[str, str] | None = None):
        self._urls = urls
        self._selection_names: dict[str, str] | None = None

    @property
    def urls(self) -> OrderedDict[str, str]:
        if self._urls is None:
            element = get_htmlelement(self._stations_url)
            self._urls = self._extract(element)
        if self._selection_names is None:
            self._selection_names = self._build_selection_names(self._urls)
        return self._urls.copy()

    def select(self, name: str) -> "Station":
        urls = self.urls
        assert self._selection_names is not None
        canonical_name = self._selection_names.get(
            _normalise_station_name(name)
        )
        if canonical_name is None:
            raise InvalidStationError(name)
        return Station(canonical_name, urls[canonical_name])

    @staticmethod
    def _extract(element: html.HtmlElement) -> OrderedDict[str, str]:
        urls: OrderedDict[str, str] = OrderedDict()

        for module in _get_experience_modules(element):
            if module.get("id") not in {
                "national_and_regional_stations",
                "local_stations",
            }:
                continue

            for station in module.get("data", []):
                network = station.get("network") or {}
                network_id = network.get("id")
                if not network_id:
                    continue
                station_name = _station_name_from_network(network)
                urls[station_name] = urljoin(
                    BBC_BASE_URL, f"/sounds/schedules/{network_id}"
                )

        if not urls:
            raise ValueError("station details not found in HTML element")
        return urls

    @staticmethod
    def _build_selection_names(urls: OrderedDict[str, str]) -> dict[str, str]:
        selection_names: dict[str, str] = {}
        for canonical_name in urls:
            for candidate in _station_name_candidates(canonical_name):
                selection_names.setdefault(
                    _normalise_station_name(candidate), canonical_name
                )
        return selection_names

    def __repr__(self) -> str:
        return f"Stations(urls={repr(self._urls)})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Stations) and self._urls == other._urls


class Station:
    """Represents a single radio station."""

    def __init__(self, name: str, url: str):
        self._name = name
        self._url = url

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f"Station(name={repr(self._name)}, url={repr(self._url)})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Station)
            and self._name == other._name
            and self._url == other._url
        )


class Schedule:
    """Represents a radio station schedule."""

    def __init__(self, station: Station, date: str):
        self._programmes = None
        self._station = station

        try:
            dt.date.fromisoformat(date)
        except ValueError as exc:
            raise InvalidDateError(f"invalid date: {date}") from exc
        self._date = date

    @property
    def programmes(self) -> list["Programme"]:
        if self._programmes is None:
            element = get_htmlelement(self._construct_url())
            self._programmes = self._extract(element)
        return copy.deepcopy(self._programmes)

    @property
    def station(self) -> Station:
        return self._station

    @property
    def date(self) -> str:
        return self._date

    def _construct_url(self) -> str:
        return f"{self._station.url}/{self._date}"

    @staticmethod
    def _extract(element: html.HtmlElement) -> list["Programme"]:
        schedule_items = []
        for module in _get_experience_modules(element):
            if module.get("id") == "schedule_items":
                schedule_items.extend(module.get("data", []))

        if not schedule_items:
            raise ValueError("schedule details not found in HTML element")

        programmes = []
        for schedule_item in schedule_items:
            playable_item = schedule_item.get("playable_item") or {}
            titles = playable_item.get("titles") or schedule_item.get(
                "titles", {}
            )
            synopses = playable_item.get("synopses") or schedule_item.get(
                "synopses", {}
            )
            container = playable_item.get("container") or {}
            identifier = playable_item.get("id") or schedule_item.get("id")
            series_name = container.get("title") or titles.get("primary")
            programme_name = (
                titles.get("secondary")
                or titles.get("entity_title")
                or titles.get("primary")
            )
            description = (
                synopses.get("long")
                or synopses.get("medium")
                or synopses.get("short")
            )

            programmes.append(
                Programme(
                    start_date=schedule_item.get("start"),
                    series_name=series_name,
                    name=programme_name,
                    description=description,
                    identifier=identifier,
                    url=(
                        f"{BBC_BASE_URL}/programmes/{identifier}"
                        if identifier is not None
                        else None
                    ),
                )
            )

        return programmes

    def __str__(self) -> str:
        return (
            "<Schedule "
            f"_station={repr(self._station)} _date={repr(self._date)}>"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Schedule)
            and self._programmes == other._programmes
            and self._station == other._station
            and self._date == other._date
        )


class Programme:
    """Represents a radio programme."""

    def __init__(self, **kwargs: str | None):
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

        for key in self._info:
            value = kwargs.get(key)
            if value is not None:
                self._info[key] = value

    @property
    def info(self) -> OrderedDict[str, str | None]:
        return self._info.copy()

    def __repr__(self) -> str:
        return f"Programme({repr(dict(self._info))})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Programme) and self._info == other._info


def _get_experience_modules(element: html.HtmlElement) -> list[dict[str, Any]]:
    next_data_text = element.xpath(NEXT_DATA_XPATH)
    if not next_data_text:
        raise ValueError("BBC page data not found in HTML element")

    payload = json.loads(next_data_text[0])
    queries = (
        payload.get("props", {})
        .get("pageProps", {})
        .get("dehydratedState", {})
        .get("queries", [])
    )

    modules = []
    for query in queries:
        data = query.get("state", {}).get("data", {})
        modules.extend(data.get("data", []))
    return modules


def _station_name_from_network(network: dict[str, Any]) -> str:
    network_id = network.get("id")
    if network_id in STATION_NAME_OVERRIDES:
        return STATION_NAME_OVERRIDES[network_id]

    short_title = network.get("short_title")
    if not short_title:
        short_title = str(network_id).replace("_", " ").title()

    if short_title.startswith("BBC "):
        return short_title

    return f"BBC {short_title}"


def _station_name_candidates(name: str) -> list[str]:
    candidates = [name]
    if name.startswith("BBC "):
        candidates.append(name.removeprefix("BBC "))
    else:
        candidates.append(f"BBC {name}")

    for alias, canonical_name in STATION_ALIASES.items():
        if canonical_name == name:
            candidates.append(alias)

    return [candidate for candidate in candidates if candidate]


def _normalise_station_name(name: str) -> str:
    return " ".join(name.split()).casefold()


def get_htmlelement(url: str) -> html.HtmlElement:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()

    element = html.fromstring(response.text)

    parsed_url = urlparse(response.url)
    base_url = urlunparse(
        parsed_url._replace(path="", params="", query="", fragment="")
    )
    element.make_links_absolute(base_url)
    return element
