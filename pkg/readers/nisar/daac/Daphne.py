# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .NISAR import NISAR

# parts
from . import tokens


# the Daphne product descriptor
class Daphne(NISAR, family="qed.readers.nisar.daac.daphne"):
    """
    The Daphne product descriptor
    """

    # literals
    extension = tokens.extension()

    # my tokens
    scid = tokens.spacecraft()
    station = tokens.station()
    antenna = tokens.antenna()
    mode = tokens.mode()
    orbit = tokens.orbit()
    receiver = tokens.receiver()
    hdrr = tokens.hdrr()
    priority = tokens.priority()
    year = tokens.year()
    day = tokens.day()
    hour = tokens.hour()
    minute = tokens.minute()
    second = tokens.second()
    nanosecond = tokens.nanosecond()
    downlink = tokens.downlink()

    # data
    product = "Daphne"

    # implementation details
    @classmethod
    def sequencer(cls):
        """
        Generate the sequence of token names as they appear in valid granule ids of my type
        """
        # whatever my superclass has
        yield from super().sequencer()
        # plus all of mine
        yield from [
            # the spacecraft id
            "scid",
            # separator
            "separator",
            # ground stations
            "station",
            # separator
            "separator",
            # antenna
            "antenna",
            # separator
            "separator",
            # mode: "00" for jpl,  or "01" for isro
            "mode",
            # separator
            "separator",
            # the 5-digit absolute orbit number
            "orbit",
            # separator
            "separator",
            # the 2-digit receiver id
            "receiver",
            # separator
            "separator",
            # the high data rate receiver input channel
            "hdrr",
            # separator
            "separator",
            # the priority group
            "priority",
            # separator
            "separator",
            # the year of file creation
            "year",
            # separator
            "separator",
            # the ordinal day within the year of file creation
            "day",
            # separator
            "separator",
            # the hour of file creation
            "hour",
            # separator
            "separator",
            # the minute of file creation
            "minute",
            # separator
            "separator",
            # the second of file creation
            "second",
            # separator
            "separator",
            # the nanosecond of file creation
            "nanosecond",
            # the extension marker
            "extension",
            # the virtual channel
            "downlink",
        ]
        # all done
        return


# end of file
