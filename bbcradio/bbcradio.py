#!/usr/bin/env python3
# encoding: utf-8
"""
bbcradio.py: Unofficial API client for the BBC Radio schedules.
"""
import logging
from collections import OrderedDict

import requests
import requests_cache
from lxml import html

# TODO: remove when finished writing code.
requests_cache.install_cache("dev_cache")


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


class Schedule:
    pass


def main():
    """ Temporary main function """
    logging.basicConfig(level=logging.DEBUG)
    stations = Stations()
    print(stations.select("BBC Radio 1"))
    for name, url in stations.urls.items():
        print(",".join([name, url]))


if __name__ == "__main__":
    main()
