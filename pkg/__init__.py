# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# import and publish pyre symbols
from pyre import (
    # protocols, components, traits, and their infrastructure
    schemata,
    constraints,
    properties,
    protocol,
    component,
    foundry,
    # decorators
    export,
    provides,
    # the manager of the pyre runtime
    executive,
    # support for concurrency
    nexus,
    # support for workflows, products, and factories
    flow,
    # shells
    application,
    plexus,
    # miscellaneous
    filesystem,
    patterns,
    primitives,
    tracking,
    units,
    timers,
    weaver,
    xml,
    # hdf5 support
    h5,
    # bindings of things
    libpyre,
)

# register the package with the framework
package = executive.registerPackage(name="qed", file=__file__)
# save the geography
home, prefix, defaults = package.layout()


# publish the local modules
# basic functionality
from . import meta  # package meta-data
from . import exceptions  # the exception hierarchy

# the bindings
from .ext import libqed, libqed_cuda

# protocols
from . import protocols

# support for data archives
from . import archives

# support for data types, controllers, and readers
from . import datatypes
from . import controllers
from . import readers

# schema
from . import gql

# user interfaces
from . import shells  # the supported application shells
from . import cli  # the command line interface
from . import ux  # support for the web client

# inspectors
from . import inspect


# administrivia
def copyright():
    """
    Return the copyright note
    """
    # pull and print the meta-data
    return print(meta.header)


def license():
    """
    Print the license
    """
    # pull and print the meta-data
    return print(meta.license)


def built():
    """
    Return the build timestamp
    """
    # pull and return the meta-data
    return meta.date


def credits():
    """
    Print the acknowledgments
    """
    return print(meta.acknowledgments)


def version():
    """
    Return the version
    """
    # pull and return the meta-data
    return meta.version


# end of file
