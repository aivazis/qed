# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# external
import math
# support
import qed

# superclass
from .Controller import Controller


# a mixin for a channel with rel values in a linear range
class Value(Controller, family="qed.controllers.value"):
   """
   Configuration for a channel with data in a linear range
   """


   # user configurable state
   value = qed.properties.float(default=0.5)
   value.doc = "the chosen value"

   min = qed.properties.float(default=0.0)
   min.doc = "the smallest possible value"

   max = qed.properties.float(default=1.0)
   max.doc = "the largest possible value"


   # interface
   def updateValue(self, value):
      """
      Update my state with new values for the range
      """
      # update my state
      self.value = value
      # and let the caller know
      return True


   # constants
   tag = "value"


# end of file
