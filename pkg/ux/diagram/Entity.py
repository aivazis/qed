# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import uuid


# the base entity
class Entity:
    """
    The base class for all diagram entities
    """

    # constants
    @classmethod
    def typename(cls):
        """
        Build a suable type name
        """
        # let's see whether this is sufficient
        return cls.__name__

    # public data
    @property
    def relay(self):
        # build a {relay} node id
        return f"{self.typename()}:{self.eid}"

    # interface
    @staticmethod
    def relayToEid(relay):
        """
        Extract my {typename} and {eid} from my {relay} id
        """
        # parse
        typename, hex = relay.split(":")
        # convert the {hex} key into a {uuid}
        eid = uuid.UUID(hex=hex)
        # pack and ship
        return typename, eid

    # metamethods
    def __init__(self, name=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # all nodes have their own ids
        self.eid = uuid.uuid1()
        # record my name
        self.name = name
        # all done
        return

    def __str__(self):
        # build my name
        name = f" {self.name}" if self.name is not None else ""
        # and my tag
        tag = str(self.eid)[:8]
        # render my {typename} and my {uuid}
        return f"{self.typename()}{name} '{tag}'"


# end of file
