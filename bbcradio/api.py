# encoding: utf-8

"""Helpers for retrieving BBC radio station schedules."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re
from collections import OrderedDict
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests

BBC_BASE_URL = "https://www.bbc.co.uk"
DEFAULT_TIMEOUT = 30
DEFAULT_HEADERS = {
    "User-Agent": (
        "bbc-radio-schedules/0.2.0 "
        "(https://github.com/StevenMaude/bbc-radio-schedules)"
    )
}


class InvalidStationError(Exception):
    """Raised when an invalid station is selected from Stations."""


class InvalidDateError(Exception):
    """Raised if a supplied date is not YYYY-MM-DD format."""


class _StationsHTMLParser(HTMLParser):
    """Extract station names and schedule URLs from a schedules index page."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.urls: "OrderedDict[str, str]" = OrderedDict()
        self._current_anchor: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a":
            self._current_anchor = {
                "href": attrs_dict.get("href"),
                "text": [],
                "alt_text": [],
            }
            return

        if tag == "img" and self._current_anchor is not None:
            alt_text = _clean_text(attrs_dict.get("alt"))
            if alt_text:
                self._current_anchor["alt_text"].append(alt_text)

    def handle_data(self, data: str) -> None:
        if self._current_anchor is None:
            return

        text = _clean_text(data)
        if text:
            self._current_anchor["text"].append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_anchor is None:
            return

        href = self._current_anchor.get("href")
        if not href:
            self._current_anchor = None
            return

        absolute_url = _make_absolute_url(href, self.base_url)
        path = urlsplit(absolute_url).path.rstrip("/")
        root_path = urlsplit(self.base_url).path.rstrip("/")
        if path in {"", root_path} or (
            "/sounds/schedules/" not in path and not path.startswith("/schedules/")
        ):
            self._current_anchor = None
            return

        station_name = next(iter(self._current_anchor["alt_text"]), None)
        if station_name is None:
            station_name = _clean_text(" ".join(self._current_anchor["text"]))

        if station_name:
            self.urls[station_name] = href

        self._current_anchor = None


class _JSONScriptParser(HTMLParser):
    """Collect JSON payloads embedded in script tags."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.payloads: list[str] = []
        self._current_payload: list[str] | None = None
        self._capture_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return

        attrs_dict = {key.lower(): value for key, value in attrs}
        script_type = (attrs_dict.get("type") or "").lower()
        script_id = attrs_dict.get("id") or ""
        self._capture_script = (
            script_type == "application/ld+json" or script_id == "__NEXT_DATA__"
        )
        if self._capture_script:
            self._current_payload = []

    def handle_data(self, data: str) -> None:
        if self._current_payload is not None:
            self._current_payload.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "script" or self._current_payload is None:
            self._capture_script = False
            return

        payload = "".join(self._current_payload).strip()
        if payload:
            self.payloads.append(payload)

        self._capture_script = False
        self._current_payload = None


class Stations:
    """Represents a collection of radio stations."""

    _stations_url = "https://www.bbc.co.uk/sounds/schedules"

    def __init__(self, urls: OrderedDict[str, str] | None = None):
        self._urls = urls

    @property
    def urls(self) -> OrderedDict[str, str]:
        if self._urls is None:
            document = get_document(self._stations_url)
            extracted_urls = self._extract(document, base_url=self._stations_url)
            self._urls = OrderedDict(
                (name, _make_absolute_url(url, self._stations_url))
                for name, url in extracted_urls.items()
            )
        return self._urls.copy()

    def select(self, name: str) -> "Station":
        url = self.urls.get(name)
        if url is None:
            raise InvalidStationError(name)
        return Station(name, url)

    @staticmethod
    def _extract(
        document: str, base_url: str = BBC_BASE_URL
    ) -> OrderedDict[str, str]:
        parser = _StationsHTMLParser(base_url=base_url)
        parser.feed(document)
        parser.close()

        if not parser.urls:
            raise ValueError("station URLs not found in schedules page")

        return parser.urls.copy()

    def __repr__(self) -> str:
        return f"Stations(urls={self._urls!r})"

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
        return f"Station(name={self._name!r}, url={self._url!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Station)
            and self._name == other._name
            and self._url == other._url
        )


class Schedule:
    """Represents a radio station schedule."""

    def __init__(self, station: Station, date: str):
        self._programmes: list[Programme] | None = None
        self._station = station

        try:
            dt.date.fromisoformat(date)
        except ValueError as exc:
            raise InvalidDateError(f"invalid date: {date}") from exc

        self._date = date

    @property
    def programmes(self) -> list["Programme"]:
        if self._programmes is None:
            last_error: Exception | None = None
            for url in self._construct_urls():
                try:
                    document = get_document(url)
                    programmes = self._extract(document)
                except requests.HTTPError as exc:
                    last_error = exc
                    if exc.response is not None and exc.response.status_code == 404:
                        continue
                    raise
                except ValueError as exc:
                    last_error = exc
                    continue

                self._programmes = programmes
                break

            if self._programmes is None:
                if last_error is not None:
                    raise last_error
                raise ValueError("unable to retrieve schedule programmes")

        return copy.deepcopy(self._programmes)

    @property
    def station(self) -> Station:
        return self._station

    @property
    def date(self) -> str:
        return self._date

    def _construct_url(self) -> str:
        return next(iter(self._construct_urls()))

    def _construct_urls(self) -> list[str]:
        base_url = self._station.url.rstrip("/")
        candidate_urls = [
            f"{base_url}/{self._date.replace('-', '/')}",
            f"{base_url}/{self._date}",
        ]
        unique_urls = []
        seen_urls = set()
        for url in candidate_urls:
            if url not in seen_urls:
                unique_urls.append(url)
                seen_urls.add(url)
        return unique_urls

    @staticmethod
    def _extract(document: str) -> list["Programme"]:
        programmes = []
        seen_programmes = set()

        for payload in _extract_embedded_json(document):
            for item in _iter_schedule_items(payload):
                start_date = _extract_start_date(item)
                if not start_date:
                    continue

                programme_details = _extract_programme_details(item)
                if not any(programme_details.values()):
                    continue

                programme = Programme(start_date=start_date, **programme_details)
                programme_key = (
                    programme.info["start_date"],
                    programme.info["identifier"],
                    programme.info["url"],
                    programme.info["name"],
                )
                if programme_key not in seen_programmes:
                    programmes.append(programme)
                    seen_programmes.add(programme_key)

        if not programmes:
            raise ValueError("schedule details not found in document")

        return programmes

    def __str__(self) -> str:
        return f"<Schedule _station={self._station!r} _date={self._date!r}>"

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
        return f"Programme({dict(self._info)!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Programme) and self._info == other._info


def _clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _make_absolute_url(url: str, base_url: str) -> str:
    absolute_url = urljoin(base_url, url)
    parts = urlsplit(absolute_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


def _extract_embedded_json(document: str) -> list[Any]:
    parser = _JSONScriptParser()
    parser.feed(document)
    parser.close()

    payloads = list(parser.payloads)
    payloads.extend(_extract_js_object_assignments(document))

    json_payloads = []
    for payload in payloads:
        try:
            json_payloads.append(json.loads(payload))
        except json.JSONDecodeError:
            continue
    return json_payloads


def _extract_js_object_assignments(document: str) -> list[str]:
    patterns = [
        r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;",
        r"window\.__INITIAL_DATA__\s*=\s*(\{.*?\})\s*;",
    ]
    payloads = []
    for pattern in patterns:
        payloads.extend(re.findall(pattern, document, flags=re.DOTALL))
    return payloads


def _iter_schedule_items(payload: Any) -> list[dict[str, Any]]:
    items = []
    stack = [payload]
    seen_ids = set()

    while stack:
        current = stack.pop()
        if isinstance(current, (dict, list)):
            object_id = id(current)
            if object_id in seen_ids:
                continue
            seen_ids.add(object_id)

        if isinstance(current, list):
            stack.extend(reversed(current))
            continue

        if not isinstance(current, dict):
            continue

        if _extract_start_date(current):
            items.append(current)

        for value in current.values():
            if isinstance(value, (dict, list)):
                stack.append(value)

    return items


def _extract_start_date(item: dict[str, Any]) -> str | None:
    return _first_text(
        item.get("startDate"),
        item.get("start_date"),
        _nested_value(item, "publication", "startDate"),
        _nested_value(item, "publication", "start_date"),
        _nested_value(item, "broadcast", "startDate"),
        _nested_value(item, "broadcast", "start_date"),
        _nested_value(item, "workPresented", "publication", "startDate"),
        _nested_value(item, "item", "publication", "startDate"),
    )


def _extract_programme_details(item: dict[str, Any]) -> dict[str, str | None]:
    nested_programme = _first_mapping(
        item.get("workPresented"),
        item.get("item"),
        item.get("programme"),
        item.get("episode"),
        item.get("broadcastOf"),
    )
    programme_source = nested_programme or item

    series_name = _first_text(
        _nested_value(programme_source, "partOfSeries", "name"),
        _nested_value(programme_source, "isPartOf", "name"),
        _nested_value(item, "partOfSeries", "name"),
        _nested_value(item, "isPartOf", "name"),
        _nested_value(programme_source, "partOfSeason", "partOfSeries", "name"),
    )

    name = _first_text(
        programme_source.get("name"),
        _nested_value(programme_source, "title"),
        _nested_value(programme_source, "titles", "primary"),
        _nested_value(item, "name"),
        _nested_value(item, "title"),
    )

    description = _first_text(
        programme_source.get("description"),
        _nested_value(programme_source, "titles", "secondary"),
        _nested_value(programme_source, "shortSynopsis"),
        _nested_value(item, "description"),
        _nested_value(item, "shortSynopsis"),
    )

    url = _first_text(
        programme_source.get("url"),
        programme_source.get("sameAs"),
        item.get("url"),
        item.get("sameAs"),
    )
    if url is not None:
        url = _make_absolute_url(url, BBC_BASE_URL)

    identifier = _first_text(
        programme_source.get("identifier"),
        programme_source.get("pid"),
        item.get("identifier"),
        item.get("pid"),
        _identifier_from_url(url),
    )

    return {
        "series_name": series_name,
        "name": name,
        "description": description,
        "identifier": identifier,
        "url": url,
    }


def _first_mapping(*values: Any) -> dict[str, Any] | None:
    for value in values:
        if isinstance(value, dict):
            return value
    return None


def _nested_value(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_text(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str):
            text = _clean_text(value)
            if text:
                return text
    return None


def _identifier_from_url(url: str | None) -> str | None:
    if url is None:
        return None

    match = re.search(r"/programmes/([^/?#]+)", url)
    if match is None:
        return None
    return match.group(1)


def get_document(url: str) -> str:
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.text
