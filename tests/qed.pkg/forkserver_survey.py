#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a fleet whose teams recruit through the forkserver makes first contact with a
product: the survey runs on a crew member forked by the helper, not by this process, and comes
back with what the product holds
"""

# externals
import os

# support
import journal
import pyre
import qed

# the unit of time
from pyre.units.SI import second


# the application; the helper runs a copy of it, so it has to be one
class Survey(pyre.application, family="tests.qed.forkserver.survey"):
    """
    An application that stages a product on a fleet that recruits through the forkserver
    """

    # interface
    @pyre.export
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # the product: the flat fixture next to this driver
        product = pyre.primitives.path(__file__).parent / "c16.dat"
        # a passive reader for it
        reader = qed.readers.native.flat(
            name="forkserver.flat", uri=f"file:{product}", shape=(65, 65), cell="c16"
        )
        # the fleet, with an event loop of its own
        fleet = qed.nexus.fleet(name="forkserver.fleet")
        fleet.dispatcher = pyre.ipc.newPSL()
        # whose teams recruit through the helper
        fleet.recruiter = qed.nexus.forkserver()
        # the outcome drop box
        outcomes = []

        # the delivery callback
        def deliver(result, error):
            """
            Record the outcome and stop the event loop
            """
            # file the report
            outcomes.append((result, error))
            # and wind down
            fleet.dispatcher.stop()
            # all done
            return

        # the alarm that ends the wait if the survey never comes back
        def expire(timestamp):
            """
            Stop the event loop
            """
            # stop
            fleet.dispatcher.stop()
            # and do not reschedule
            return None

        # send the reader for first contact
        fleet.stage(reader=reader, callback=deliver)
        # give the crew plenty of time
        fleet.dispatcher.alarm(interval=60 * second, call=expire)
        # and wait
        fleet.dispatcher.watch()

        # the survey came back
        assert len(outcomes) == 1, outcomes
        # without an error
        record, error = outcomes[0]
        assert error is None, error
        # with what the product holds
        assert len(record.findings) == 1, record.findings
        # the members of the builders of the reader, who make first contact
        team = fleet.builders(reader=reader.pyre_name)
        pids = [crew.pid for crew in team.crews()]
        # exist
        assert pids
        # and none of them is my child, since the helper forked them
        for pid in pids:
            # carefully
            try:
                # there should be nothing to wait for
                os.waitpid(pid, os.WNOHANG)
            # which is how it should be
            except ChildProcessError:
                # good
                continue
            # otherwise, it is my child after all
            assert False, f"member {pid} is a child of this process"

        # send everybody home
        fleet.disband()
        # including the helper
        fleet.recruiter.stop()

        # all done
        return 0


# main
if __name__ == "__main__":
    # the readers complain about the missing web documents; this driver is not the app
    journal.warning("qed.cli").deactivate()
    # instantiate
    app = Survey(name="forkserver_survey")
    # invoke
    status = app.run()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
