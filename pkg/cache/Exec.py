# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import os
import itertools

# my protocol
from .Recruiter import Recruiter


# fork/exec as a team member creation strategy
class Exec(qed.component, family="qed.nexus.recruiters.exec", implements=Recruiter):
    """
    Use the {fork}+{exec} system calls to create new team members
    """

    # protocol obligations
    @qed.implements
    def recruit(self, app, team, **kwds):
        """
        Recruit members for the {team}
        """
        # ask {team} for the number of required members
        vacancies = team.vacancies()
        # go through the vacancies
        for _ in range(vacancies):
            # creating {team} members and deploying them
            yield self.deploy(app=app, team=team, **kwds)
        # all done
        return

    @qed.implements
    def deploy(self, app, team, **kwds):
        """
        Create a new team member
        """
        # make a member id
        badge = next(self.counter)
        # build the communication channels
        manager, crew = qed.ipc.pipe()
        # clone the current process
        pid = os.fork()

        # on the crew side
        if pid == 0:
            # close the manager channel
            manager.close()
            # tell the team we are creating a new team member
            app, argv = team.exec(app=app, badge=badge, channel=crew)
            # deploy
            os.execv(app, argv)
            # UNREACHABLE

        # on the manager side, close the crew member's channel
        crew.close()
        # let the team know that there is a new recruit
        return team.register(
            # the application context
            app=app,
            # the worker process id
            wid=pid,
            # the badge number
            badge=badge,
            # and the communication channel
            channel=manager,
        )

    @qed.implements
    def dismiss(self, team, crew, **kwds):
        """
        The {team} manager has dismissed the given {crew} member
        """
        # harvest the {crew} worker status
        _, code = os.waitpid(crew.wid, 0)
        # interpret the exit code
        status = os.waitstatus_to_exitcode(code)
        # and hand off the process exit status
        return status

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # initialize my counter
        self.counter = itertools.count()
        # all done
        return


# end of file
