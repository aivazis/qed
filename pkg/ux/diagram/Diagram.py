# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal

# the nodes
from .Entity import Entity
from .Factory import Factory
from .Slot import Slot


# flow graph entities and their layout
class Diagram:
    """
    The server side representation of the flow diagram
    """

    # public data
    @property
    def connectors(self):
        """
        Iterate over all known connectors
        """
        # go through all my slots
        for slot in self.slots:
            # and return all of their connections
            yield from slot.connections()
        # all done
        return

    # interface
    @staticmethod
    def relayToEid(relay):
        """
        Extract the {typename} and {eid} from a {relay} id
        """
        # {entities} know how to do this
        return Entity.relayToEid(relay)

    def findNode(self, relay):
        """
        Look up a node given its {relay} id
        """
        # parse the {relay} id
        typename, eid = self.relayToEid(relay=relay)
        # look up the node
        node = self.nodes.get(eid)

        # make sure it exists
        if node is None:
            # if not, we have a problem that's almost certainly a bug
            channel = journal.firewall("qed.ux.diagram.nodes")
            # so complain
            channel.line(f"while looking up '{relay}'")
            channel.line(f"in the diagram for {self.flow}")
            channel.log(f"node '{eid}' not found")
            # in case firewalls aren't fatal, return the found node
            return node

        # make sure it's the right type
        if node.typename() != typename:
            # if not, we have a problem that's almost certainly a bug
            channel = journal.firewall("qed.ux.diagram.nodes")
            # so complain
            channel.line(f"while looking up '{relay}'")
            channel.line(f"in the diagram for {self.flow}")
            channel.log(f"type mismatch: retrieved node is '{typename}'")
            # in case firewalls aren't fatal, return the found node
            return node

        # all done
        return node

    # new nodes
    def addFactory(self, factory, position):
        """
        Add a factory to the flow
        """
        # place the factory in the flow
        self.flow.factories.add(factory)
        # build an entity
        entity = Factory(factory=factory, position=position)
        # its slots
        slots = entity.slots
        # and its connectors
        connectors = list(entity.connections())

        # make a pile
        labels = []
        # add the entity labels
        labels.extend(entity.labels)
        # go through the connetors
        for connector in connectors:
            # and add their labels to the pile
            labels.extend(connector.labels)

        # i maintain a set of all factories
        self.factories.add(entity)
        # and all slots
        self.slots |= slots

        # update my node index: it keeps track of the factory itself
        self.nodes[entity.eid] = entity
        # its slots
        self.nodes.update((slot.eid, slot) for slot in slots)
        # and the new labels
        self.nodes.update((label.eid, label) for label in labels)

        # update my layout
        self.layout[entity.position] = entity
        self.layout.update((slot.position, slot) for slot in slots)

        # return the new factory
        return entity, labels, slots, connectors

    def addProduct(self, product, position):
        """
        Add a product to the flow
        """
        # place the product in the flow
        self.flow.products.add(product)
        # build an entity
        entity = Slot(product=product, position=position)
        # and generate its labels
        labels = entity.labels

        # i have a set of all slots
        self.slots.add(entity)

        # update my node index: it keeps track of both slots
        self.nodes[entity.eid] = entity
        # and their labels
        self.nodes.update((label.eid, label) for label in labels)

        # update my layout
        self.layout[entity.position] = entity

        # return the new slot
        return entity, labels

    # event handlers
    def move(self, node, position):
        """
        Move {node} to a new {position}, if permitted
        """
        # if the position hasn't changed
        if position == node.position:
            # it's a legal move
            return True

        # get the current migrant node, and its original position
        migrant = self.migrant
        # if it's not the current {node}
        if migrant is not node:
            # make it so
            self.migrant = node
            # remove it from the layout
            del self.layout[node.position]

        # check whether there is somebody already there
        occupant = self.layout.get(position)
        # if so
        if occupant:
            # check whether bindings are permitted among the two nodes
            if not self.supported(node, occupant):
                # and if not, the move is illegal
                return False

        # mark whether this move caused a collision
        self.collision = occupant

        # move the node and its labels
        node.move(position=position)

        # all done
        return True

    def resolve(self, node):
        """
        Resolve any side effects of placing {node} in its current location
        """
        # clear the migration marker
        self.migrant = None
        # put the node back in the layout
        self.layout[node.position] = node

        # get the potential collision target
        dead = self.collision
        # if there was no collision
        if dead is None:
            # all done
            return None, [], []

        # otherwise, we have to compute the move side effects; first up, maintenance of
        # my indices that requires access to the stale information
        # clear the collision marker
        self.collision = None
        # remove the dead node from my slot index
        self.slots.discard(dead)
        # and my node index
        del self.nodes[dead.eid]

        # now, ask {node} to subsume the {dead} node's info
        return node.merge(other=dead)

    # metamethods
    def __init__(self, flow=None, **kwds):
        # chain up
        super().__init__(**kwds)

        # my flow
        self.flow = flow if flow is not None else qed.flow.dynamic()
        # the pile of slots
        self.slots = set()
        # factories
        self.factories = set()

        # my layout keeps track of entity locations
        self.layout = {}

        # the node index maps relay ids to diagram entities
        self.nodes = {}
        # a set of labels that are not associated with any entity
        self.labels = set()

        # a record of the moving node and its initial position
        self.migrant = None, ()
        # marker that a collision among nodes was detected during a move
        self.collision = None

        # all done
        return

    # implementation details
    def supported(self, n1, n2):
        """
        Check whether a binding between {n1} and {n2} is permissible
        """
        # if either is a factory
        if isinstance(n1, Factory) or isinstance(n2, Factory):
            # the binding is not supported
            return False

        # if both are products
        if n1.product is not None and n2.product is not None:
            # the binding is not supported
            return False

        # anything else is ok
        return True

    # debugging support
    def dump(self):
        """
        Generate a report with my slots and factories
        """
        # first the flow name
        yield f"flow: {self.flow}"
        # go through my slots
        yield f"  slots:"
        for slot in self.slots:
            yield f"    {slot}"
        # go through my factories
        yield f"  factories:"
        for factory in self.factories:
            yield f"    {factory}"
        # all done
        return


# end of file
