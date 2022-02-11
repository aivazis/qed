# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.amplitude"):
   """
   Make a visualization pipeline to display the amplitude of complex values
   """


# end of file
