# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the imaginary part of complex values
class Imaginary(Channel, family="qed.channels.imaginary"):
   """
   Make a visualization pipeline to display the imaginary part of complex values
   """


# end of file
