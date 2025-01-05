# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# pull the action protocol
from ..shells import action

# and the base panel
from ..shells import command

# pull in the command decorator
from .. import foundry


# utilities
@foundry(implements=action, tip="access to S3 buckets")
def s3():
    # get the action
    from .S3 import S3

    # borrow its docstring
    __doc__ = S3.__doc__
    # and publish it
    return S3


@foundry(implements=action, tip="a collection of introspection utilities")
def inspect():
    # get the action
    from .Inspect import Inspect

    # borrow its docstring
    __doc__ = Inspect.__doc__
    # and publish it
    return Inspect


# application introspection
@foundry(implements=action, tip="information about this application")
def about():
    # get the action
    from .About import About

    # borrow its docstring
    __doc__ = About.__doc__
    # and publish it
    return About


@foundry(implements=action, tip="configuration information")
def config():
    # get the action
    from .Config import Config

    # borrow its docstring
    __doc__ = Config.__doc__
    # and publish it
    return Config


@foundry(implements=action, tip="helpful information")
def info():
    # get the action
    from .Info import Info

    # borrow its docstring
    __doc__ = Info.__doc__
    # and publish it
    return Info


# low level info useful while debugging
@foundry(implements=action, tip="debugging information")
def debug():
    # get the action
    from .Debug import Debug

    # borrow its docstring
    __doc__ = Debug.__doc__
    # and publish it
    return Debug


# command completion; no tip so it doesn't show up on the help panel
@foundry(implements=action)
def complete():
    # get the action
    from .Complete import Complete

    # and publish it
    return Complete


# end of file
