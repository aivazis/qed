# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import re

# product descriptors
from .Daphne import Daphne
from .HST_DRT import HST_DRT
from .RRST import RRST
from .RRSD import RRSD
from .RSLC import RSLC
from .GSLC import GSLC
from .GCOV import GCOV
from .SME2 import SME2
from .RIFG import RIFG
from .RUNW import RUNW
from .ROFF import ROFF
from .GUNW import GUNW
from .GOFF import GOFF


# the recognizer
class Registrar:
    """
    The keeper of the file naming conventions for the NISAR mission
    """

    # interface
    def parse(self, granule):
        """
        Determine the product type and dispatch to more specific recognizers
        """
        # extract enough metadata to figure out the type of product
        meta = self.grok(granule)
        # if the spacecraft id is present
        if meta["sid"] == "S198":
            # this a Daphne product from the download link
            handler = self.daphne
        # otherwise
        else:
            # look up the product field to see what we matched
            product = meta["product"].lower()
            # and use it to get the correct handler
            handler = getattr(self, product)
        # build the descriptor and return it
        return handler(name=f"{granule}.descriptor", granule=granule)

    # implementation details
    def grok(self, granule):
        """
        Analyze the {granule} id and extract some metadata
        """
        # initialize the metadata table
        meta = {
            "sid": "unknown",
            "band": "unknown",
            "product": "unknown",
            "level": "unknown",
        }
        # hand the name to the regex
        match = self.namingConventions.match(granule)
        # if it's not recognizable
        if not match:
            # go no further
            return meta
        # otherwise, extract some fields
        meta["sid"] = match.group("sid")
        meta["band"] = match.group("band")
        meta["product"] = match.group("product")
        meta["level"] = match.group("level")
        # all done
        return meta

    # the product type handlers
    def daphne(self, **kwds):
        """
        Build a Daphne product descriptor
        """
        # dispatch
        return Daphne(**kwds)

    def hst_drt(self, **kwds):
        """
        Convert a filename to an HST_DRT product descriptor
        """
        # dispatch to the HST_DTR factory
        return HST_DRT(**kwds)

    def rrst(self, **kwds):
        """
        Convert a filename to an RRST product descriptor
        """
        # dispatch to the RRST factory
        return RRST(**kwds)

    def rrsd(self, **kwds):
        """
        Convert a filename to an RRSD product descriptor
        """
        # dispatch to the RRSD factory
        return RRSD(**kwds)

    def rslc(self, **kwds):
        """
        Convert a filename to an RSLC product descriptor
        """
        # dispatch to the RSLC factory
        return RSLC(**kwds)

    def rifg(self, **kwds):
        """
        Convert a filename to an RIFG product descriptor
        """
        # dispatch to the RIFG factory
        return RIFG(**kwds)

    def runw(self, **kwds):
        """
        Convert a filename to an RUNW product descriptor
        """
        # dispatch to the RUNW factory
        return RUNW(**kwds)

    def roff(self, **kwds):
        """
        Convert a filename to an ROFF product descriptor
        """
        # dispatch to the ROFF factory
        return ROFF(**kwds)

    def gslc(self, **kwds):
        """
        Convert a filename to an GSLC product descriptor
        """
        # dispatch to the GSLC factory
        return GSLC(**kwds)

    def gcov(self, **kwds):
        """
        Convert a filename to an GCOV product descriptor
        """
        # dispatch to the GCOV factory
        return GCOV(**kwds)

    def gunw(self, **kwds):
        """
        Convert a filename to an GUNW product descriptor
        """
        # dispatch to the GUNW factory
        return GUNW(**kwds)

    def goff(self, **kwds):
        """
        Convert a filename to an GOFF product descriptor
        """
        # dispatch to the GOFF factory
        return GOFF(**kwds)

    def sme2(self, **kwds):
        """
        Convert a filename to an SME2 product descriptor
        """
        # dispatch to the SME2 factory
        return SME2(**kwds)

    def unknown(self, granule, **kwds):
        """
        Handler for names that don't obey the naming conventions
        """
        # make a channel
        channel = journal.warning("qed.readers.nisar.daac")
        # complain
        channel.line(f"unable to recognize '{granule}' as a NISAR data product ")
        # flush
        channel.log()
        # and bail
        return

    # the scanner
    scanner = (
        # the mission
        r"NISAR"
        # separator
        r"_"
        # followed by either
        r"("
        # the explicit spacecraft id
        r"(?P<sid>S198)"
        # or
        r"|("
        # the instrument band
        r"(?P<band>L|S)"
        # the product level
        r"(?P<level>\d)"
        # separator
        r"_"
        # processing type; not present in all products
        r"((PR|UR|OD)_)?"
        # and a product specific portion
        r"(?P<product>HST_DRT|RRST|RTLM|CRSD|RRSD|RSLC|RIFG|RUNW|ROFF|GSLC|GUNW|GOFF|GCOV|SME2)"
        # end of the canonical match
        r")"
        # done
        r")"
    )
    # the product recognizer
    namingConventions = re.compile(scanner)


# end of file
