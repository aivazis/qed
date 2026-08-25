# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the base marker for failures the client can recover from by asking again
from pyre.nexus.exceptions import RecoverableError


# the marker for a task that took its crew member down with it
class Casualty(RecoverableError):
    """
    A crew member died while carrying a task

    A death without a report means the task itself may be the killer, e.g. a request that
    crashes the native rendering pipeline; such a task must never be retried in the server
    process, whose survival is the whole point of farming work out to crews
    """


# end of file
