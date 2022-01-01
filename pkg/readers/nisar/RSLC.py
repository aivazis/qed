# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# external
import itertools
# support
import qed


# the RSLC reader
class RSLC(qed.flow.factory, family="qed.readers.nisar.rslc", implements=qed.protocols.reader):
    """
    The reader of RSLC files
    """


    # public data
    uri = qed.properties.path()
    uri.doc = "the uri of the data source"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the size of the dataset in (lines, samples)"

    selectors = qed.protocols.selectors()
    selectors.default = {
        "frequency": ["A", "B"],
        "polarization": ["HH", "HV", "VH", "VV"],
    }
    selectors.doc = "a map of selector names to their allowed values"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # grab my selectors
        selectors = self.selectors
        # autogenerate all possible selector bindings
        bindings = (
            dict(zip(selectors.keys(), values))
            for values in itertools.product(*selectors.values())
        )
        # NISAR RSLC files contain up to eight datasets; autogenerate them, for now
        for selector in bindings:
            # make a dataset
            dataset = qed.datasets.raw()
            # decorate it
            dataset.shape = self.shape
            dataset.cell = qed.datatypes.complex4()
            dataset.selector = selector
            # and attach it
            self.datasets.append(dataset)

        # all done
        return


# end of file
