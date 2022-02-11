# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.complex"):
   """
   Make a visualization pipeline to display complex values
   """


# end of file
