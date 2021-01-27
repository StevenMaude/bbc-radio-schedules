# encoding: utf-8

"""bbcradio
--------

This is a simple and unofficial API to the BBC's radio station schedules.

Copyright (c) 2021 Steven Maude
Licensed under the MIT License, see LICENSE.
"""

from .api import (
    InvalidStationError,
    InvalidDateError,
    Stations,
    Station,
    Schedule,
    Programme,
)
