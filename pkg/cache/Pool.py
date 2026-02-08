# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .Server import Server

# protocols
from .Team import Team
from .Recruiter import Recruiter


# the work distributor
class Pool(Server, family="qed.services.pool", implements=(Team, qed.nexus.service)):
    """
    A process collective that carry out a work plan
    """

    # types
    from .Badge import Badge as badge

    # user configurable state
    size = qed.properties.int()
    size.default = 1
    size.doc = "the maximum number of crew members in the team"

    recruiter = Recruiter()
    recruiter.doc = "the strategy for recruiting new team members"

    # server obligations
    @qed.implements
    def activate(self, app, dispatcher):
        """
        Enable the tile cache as a service
        """
        # chain up
        super().activate(app=app, dispatcher=dispatcher)
        # put the team together
        self.assemble(app=app, dispatcher=dispatcher, workplan=None)
        # all done
        return

    # team obligations
    @qed.implements
    def assemble(self, app, dispatcher, workplan, **kwds):
        """
        Recruit a team to execute the set of tasks in my {workplan}
        """
        # ask my recruiter to put together a team
        for badge in self.recruiter.recruit(app=app, team=self):
            # and onboard each new member
            self.onboard(app=app, dispatcher=dispatcher, badge=badge)
        # all done
        return

    @qed.implements
    def vacancies(self):
        """
        Compute how many recruits are needed to take the team to full strength
        """
        # no work plan considerations at this level; just the difference between the pool size and
        # the number of workers already deployed
        return self.size - len(self._active)

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # initialize the crew registries
        self._registered = {}
        self._active = set()
        self._retired = set()

        # all done
        return

    # implementation details
    # crew member registration
    def register(self, app, wid, badge, channel):
        """
        Register a new crew member with the given {badge} number and communication {channel}
        """
        # make a new badge
        badge = self.badge(app=app, badge=badge, wid=wid, channel=channel)
        # register it
        self._registered[badge.eid] = badge
        # and return the badge
        return badge

    def onboard(self, app, dispatcher, badge):
        """
        On board a crew member
        """
        # grab the crew member contact point
        channel = badge.contact
        # and start watching its read end
        dispatcher.whenReadReady(
            channel=channel, call=self.punchIn, badge=badge, app=app
        )
        # all done
        return

    def punchIn(self, badge, **kwds):
        """
        A crew member is reporting for duty
        """
        # add this crew member to the active duty list
        self._active.add(badge.eid)
        # don't reschedule
        return False

    def punchOut(self, badge, **kwds):
        """
        Retire this crew member
        """
        # get the badge id
        eid = badge.eid
        # remove the crew member from the active roster
        self._active.discard(eid)
        # retire
        self._retired.add(eid)
        # and shutdown the crew member's contact point
        badge.contact.close()
        # all done
        return

    # recruiter support
    def exec(self, **kwds):
        """
        Generate a crew member specification suitable for the {exec} recruiter
        """
        # don't know how to do that
        raise NotImplementedError(f"class {type(self).__name__} must implement 'exec'")


# end of file
