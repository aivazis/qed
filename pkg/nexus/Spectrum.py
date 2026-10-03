# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# the shared task core
from .Chore import Chore

# the parking place for the rendered payload
from .Spool import Spool


# the spectrum of a region, computed by a tile rendering crew
class Spectrum(Chore):
    """
    A picklable description of a request for the spectrum of a rectangle of a complex raster

    Instances are built on the team side from the live view state, and executed on the worker
    side by the crew member that picks them up, which reads the region at full resolution
    through the reader it keeps open, transforms it, and renders the result as a gray tile
    """

    # interface - worker side
    def execute(self, readers, **kwds):
        """
        Compute and render my spectrum using {readers}, the registry of data sources owned by my
        crew member
        """
        # carefully, since failures here should not poison the crew member
        try:
            # locate my reader, building it on first contact; a spectrum has no use for the
            # statistics of the datasets, so they are not sampled
            reader = self._locateReader(readers=readers, measure=False)
            # find the dataset i'm after
            dataset = self._locateDataset(reader=reader)
            # the region is read at full resolution, straight off the product
            data, _, _ = dataset.resolve(zoom=(0, 0))
            # read it, transform it, and render the result
            picture = qed.libqed.nisar.slc.fft(
                source=data,
                datatype=dataset.datatype.htype,
                origin=self.origin,
                shape=self.shape,
                range=self.range,
            )
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy
            raise self.RecoverableError(description=str(error)) from None
        # on success, park the picture in a spool; its descriptor travels as ancillary data on
        # the crew channel, so the payload itself never crosses the wire
        return Spool.stash(data=memoryview(picture))

    # metamethods
    def __init__(self, view, origin, shape, range=60.0, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the region
        self.origin = tuple(origin)
        self.shape = tuple(shape)
        # and the decibels below the strongest frequency that span the gray scale
        self.range = float(range)
        # get the data source of the view
        reader = view.reader
        # record its name; it keys the worker side reader registry
        self.reader = reader.pyre_name
        # and its family, so workers can rebuild it
        self.factory = reader.pyre_family()
        # harvest the reader configuration needed to reopen the data source
        self.config = self._harvestReader(reader=reader)
        # the dataset is identified by its selector, which is stable across reader rebuilds
        self.selector = dict(view.dataset.selector)
        # record the dataset name as well, for the diagnostics
        self.dataset = view.dataset.pyre_name
        # my identity is the complete request specification, so equal requests share a single
        # execution and a cached picture; access credentials are not part of what is computed,
        # so a rotated token must not invalidate cached work
        spec = {name: value for name, value in self.config.items() if name != "credentials"}
        self.identity = self._freeze(
            value=(
                "spectrum",
                self.reader,
                self.factory,
                spec,
                self.selector,
                self.origin,
                self.shape,
                self.range,
            )
        )
        # all done
        return


# end of file
