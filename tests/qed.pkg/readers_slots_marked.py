#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Every facility of a reader component that is typed by a specification is a slot of the pipeline
diagram, so it must say which side of its factory it is on: marked as an input, an output, or
both; settings are typed by plain protocols
"""

# externals
import importlib
import pkgutil

# support
import pyre
import qed


# the driver
def test() -> None:
    """
    Visit every component class under {qed.readers} and check the marks of its slots
    """
    # the classes, by their qualified name, so each one is checked once
    classes = {}
    # go through the modules of the readers
    for info in pkgutil.walk_packages(qed.readers.__path__, prefix="qed.readers."):
        # load it
        module = importlib.import_module(info.name)
        # go through what it holds
        for obj in vars(module).values():
            # skip anything that is not a component class
            if not isinstance(obj, type) or not issubclass(obj, pyre.component):
                # on to the next
                continue
            # skip the ones it borrows from elsewhere
            if not obj.__module__.startswith("qed.readers."):
                # on to the next
                continue
            # file it
            classes[f"{obj.__module__}.{obj.__name__}"] = obj
    # there must be some
    assert classes
    # the slots that are on neither side
    unmarked = []
    # go through the classes
    for name, cls in sorted(classes.items()):
        # and their facilities
        for trait in cls.pyre_facilities():
            # a facility typed by a specification is a slot
            if not issubclass(trait.protocol, qed.flow.specification):
                # anything else is a setting
                continue
            # a slot that is neither an input nor an output
            if not trait.input and not trait.output:
                # is a mistake
                unmarked.append(f"{name}.{trait.name}")
    # there must be none
    assert not unmarked, unmarked
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
