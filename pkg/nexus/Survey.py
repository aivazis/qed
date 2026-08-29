# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the shared task core
from .Chore import Chore

# what a survey reports
from .Discovery import Discovery


# the unit of work that establishes first contact with a data product
class Survey(Chore):
    """
    A picklable request to establish first contact with a data product

    The survey is the only first contact that happens anywhere in the system: a crew member
    builds the reader from its recipe, opens the product, walks its structure, and ships
    back a discovery record. Discovery is sequential work, so a survey employs exactly one
    worker and seeks no speedup within a product; what the arrangement buys is placement,
    since the event loop never blocks, a defective file harms only the worker that opened
    it, products survey concurrently with one another, and the worker that performed the
    examination keeps the product open, ready to render
    """

    # interface - worker side
    def execute(self, readers, **kwds):
        """
        Establish first contact with my data product using {readers}, the registry of data
        sources owned by my crew member, and report what it holds
        """
        # carefully, since a malformed or unreachable product should not poison the crew
        # member; the reader rebuild opens the file, which is the whole point of the task
        try:
            # locate my reader, building and opening it on first contact
            reader = self._locateReader(readers=readers)
            # and compose the record of what it found
            discovery = Discovery.compose(reader=reader)
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy; the team
            # side turns it into the {failed} lifecycle state, error retained
            raise self.RecoverableError(description=str(error)) from None
        # hand off the report
        return discovery

    # metamethods
    def __init__(self, reader, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the reader name; it keys the worker side reader registry
        self.reader = reader.pyre_name
        # and its family, so workers can rebuild it
        self.factory = reader.pyre_family()
        # harvest the reader configuration needed to open the data source
        self.config = self._harvestReader(reader=reader)
        # my identity is the product specification: two surveys of the same product with
        # the same settings are the same work, so a repeat request joins the one in flight
        # rather than opening the file a second time
        # access credentials are not part of what is discovered: a rotated token must not
        # make an in-flight survey look like different work
        spec = {
            name: value for name, value in self.config.items() if name != "credentials"
        }
        self.identity = self._freeze(value=(self.reader, self.factory, spec))
        # all done
        return


# end of file
