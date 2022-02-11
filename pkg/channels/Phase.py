# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# superclass
from .Channel import Channel


# a channel for displaying the phase of complex values
class Phase(Channel, family="qed.channels.phase"):
   """
   Make a visualization pipeline to display the phase of complex values
   """


# end of file
