# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import re


# the recognizer
class Registrar:
    """
    The keeper of the file naming conventions for the NISAR mission
    """

    # interface
    def parse(self, granule):
        """
        Determine the product type and build its descriptor; return {None} if the id is not
        recognized, and let {daac.descriptor} tell the caller
        """
        # find the descriptor of the product
        factory = self.factory(granule=granule)
        # if the id does not obey the naming conventions
        if factory is None:
            # there is no descriptor to build
            return None
        # build the descriptor and return it; it is anonymous, so the configuration store holds
        # nothing on its behalf and it goes away when its clients let go of it
        return factory(granule=granule)

    def fields(self, granule):
        """
        Extract the fields of the {granule} id as strings, without building a descriptor;
        return {None} if the id is not recognized

        This is a cheap way to sift through many ids, e.g. for the ones of one cycle, before
        building descriptors for the ones that are wanted
        """
        # find the descriptor of the product
        factory = self.factory(granule=granule)
        # if the id does not obey the naming conventions
        if factory is None:
            # there are no fields to extract
            return None
        # match the id against the naming conventions of its product
        match = factory.regex.match(granule)
        # and return its fields, if it matched
        return match.groupdict() if match else None

    # implementation details
    def factory(self, granule):
        """
        Find the descriptor of the product named by the {granule} id in the {daac} package;
        return {None} if the id does not obey the naming conventions
        """
        # extract enough metadata to figure out the type of product
        meta = self.grok(granule)
        # if the spacecraft id is present
        if meta["sid"] == "S198":
            # this is a Daphne product from the download link
            product = "daphne"
        # otherwise
        else:
            # the product field names it
            product = meta["product"].lower()
        # if the id does not obey the naming conventions
        if product == "unknown":
            # there is no descriptor
            return None
        # otherwise, the {daac} package publishes the descriptor under the product name
        return getattr(qed.readers.nisar.daac, product)

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
        # otherwise, extract some fields: the spacecraft id
        meta["sid"] = match.group("sid")
        # the band
        meta["band"] = match.group("band")
        # the product
        meta["product"] = match.group("product")
        # and the processing level
        meta["level"] = match.group("level")
        # all done
        return meta

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
        r"(?P<product>HST_DRT|RRST|RRSD|RSLC|RIFG|RUNW|ROFF|GSLC|GUNW|GOFF|GCOV|SME2)"
        # end of the canonical match
        r")"
        # done
        r")"
    )
    # the product recognizer
    namingConventions = re.compile(scanner)


# end of file
