"""The ChirpStack LoRaWAN Integration - setup."""

from __future__ import annotations

import logging

from .const import (
    DETAILED_LEVEL_NUM,
    DETAILED_LEVEL_STR,
)

_LOGGER = logging.getLogger(__name__)
__version__ = "1.2.0"

# https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084
logging.addLevelName(DETAILED_LEVEL_NUM, DETAILED_LEVEL_STR)


def detail(self, message, *args, **kws):
    """Set up 'detail' logging level."""
    if self.isEnabledFor(DETAILED_LEVEL_NUM):
        self._log(DETAILED_LEVEL_NUM, message, args, **kws)


logging.Logger.detail = detail  # type: ignore[attr-defined]
# https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084
