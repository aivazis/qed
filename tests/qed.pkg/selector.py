#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise dataset selection
"""

# support
import qed


# the app
class Select(qed.application, family="qed.apps.selector"):
    """
    Exercise dataset selection
    """

    # state
    uri = qed.properties.uri(scheme="file")
    uri.default = "rslc.h5"
    uri.doc = "the path to the data product"

    frequency = qed.properties.str()
    frequency.default = "B"
    frequency.doc = "the band frequency"

    polarization = qed.properties.str()
    polarization.default = "HH"
    polarization.doc = "the dataset polarization"

    # interface
    @qed.export
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # locate the product
        path = qed.primitives.path(str(self.uri.address))
        # if the fixture has not been generated
        if not path.exists():
            # there is nothing to check
            return 0
        # unpack my state into a selector
        selector = {"frequency": self.frequency, "polarization": self.polarization}
        # make a reader
        reader = qed.readers.nisar.rslc(name=f"{self.pyre_name}.reader", uri=self.uri)
        # make first contact
        reader.open()
        # ask it for matching datasets
        for dataset in reader.select(selector=selector):
            # show me
            print(f"select: {dataset.pyre_name}: {dataset.selector}")
        # find the first one
        dataset = reader.find(selector=selector)
        # show me
        print(f"find: {dataset.pyre_name}: {dataset.selector}")
        # all done
        return


# bootstrap
if __name__ == "__main__":
    # instantiate
    app = Select(name="selector")
    # invoke
    status = app.run()
    # share
    raise SystemExit(status)


# end of file
