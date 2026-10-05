# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# the nodes
from .Entity import Entity
from .Factory import Factory
from .Slot import Slot


# flow graph entities and their layout
class Diagram(qed.component, family="qed.ux.flow.diagrams.diagram"):
    """
    The server side representation of the flow diagram
    """

    # user configurable state
    spacing = qed.properties.float()
    spacing.default = 15
    spacing.doc = "the distance between neighboring factories, enough to keep their slots apart"

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

    def locate(self, relay):
        """
        Look up a node given its {relay} id, or nothing when the id is not one of mine
        """
        # carefully, since the id comes from a client
        try:
            # parse it
            _, eid = self.relayToEid(relay=relay)
        # an id that does not parse
        except ValueError:
            # is not one of mine
            return None
        # look it up
        return self.nodes.get(eid)

    def movable(self, node):
        """
        Check whether {node} can be moved on its own: factories and slots can, the labels and
        connectors that follow them cannot
        """
        # easy enough
        return isinstance(node, (Factory, Slot))

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
        # and update the diagram
        return self.drawFactory(factory=factory, position=position)

    def fits(self, factory, position):
        """
        Check whether {factory} placed at {position} would land on free spots, along with all
        the slots it would bring
        """
        # build a throwaway entity, which places the slots of the factory around it
        entity = Factory(factory=factory, position=position)
        # the spots it would take
        spots = [entity.position] + [slot.position for slot in entity.slots]
        # it fits if none of them is taken
        return not any(spot in self.layout for spot in spots)

    def removeFactory(self, entity):
        """
        Remove the factory {entity} from the diagram and its flow, along with its connectors;
        the slots it leaves without any connections go as well, the ones other factories still
        use stay
        """
        # a factory in the middle of a move is no longer moving
        if self.migrant is entity:
            # so forget it
            self.migrant = None
        # go through its slots
        for slot in list(entity.slots):
            # and the connectors between it and the slot
            for connector in list(slot.connections(factory=entity)):
                # forget the labels of the connector
                self.forget(nodes=connector.labels)
            # detach the slot from the factory, on whichever side it was
            slot.readers.pop(entity, None)
            slot.writers.pop(entity, None)
            # a slot that nobody uses any more
            if not slot.readers and not slot.writers:
                # goes, along with its labels
                self.forget(nodes=slot.labels)
                self.forget(nodes=[slot])
        # forget the labels of the factory
        self.forget(nodes=entity.labels)
        # and the factory itself
        self.forget(nodes=[entity])
        # take it out of the flow
        self.flow.factories.discard(entity.factory)
        # all done
        return

    def forget(self, nodes):
        """
        Remove {nodes} from my indices, my layout, and my piles
        """
        # go through them
        for node in list(nodes):
            # out of the node index
            self.nodes.pop(node.eid, None)
            # out of the layout, if it holds a spot
            if self.layout.get(node.position) is node:
                # by removing it
                del self.layout[node.position]
            # and out of whichever pile it is on
            self.factories.discard(node)
            self.slots.discard(node)
            self.labels.discard(node)
        # all done
        return

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

        # get the node in the middle of a move, if any
        migrant = self.migrant
        # if it's not the current {node}
        if migrant is not node:
            # a different node left in the middle of a move, e.g. by a client that went away
            # mid-drag, lands where it was last seen before this one takes off
            if migrant is not None:
                # settle it
                self.resolve(node=migrant)
            # the current {node} is now the one on the move
            self.migrant = node
            # and leaves its spot on the layout, if it holds it
            if self.layout.get(node.position) is node:
                # by removing it
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
        # initialize my indices: the pile of slots
        self.slots = set()
        # factories
        self.factories = set()
        # my layout keeps track of entity locations
        self.layout = {}
        # the node index maps relay ids to diagram entities
        self.nodes = {}
        # a set of labels that are not associated with any entity
        self.labels = set()
        # the node in the middle of a move, if any
        self.migrant = None
        # marker that a collision among nodes was detected during a move
        self.collision = None
        # set up my flow
        self.flow = self.draw(flow=flow)
        # all done
        return

    # implementation details
    def draw(self, flow):
        """
        Traverse the {flow} graph and categorize its contents
        """
        # if it's a trivial {flow}
        if flow is None:
            # make an empty one and return it
            return qed.flow.dynamic()

        # otherwise, harvest its nodes; go through the factories in the order the data flows
        # through them
        for index, factory in enumerate(self.order(flow=flow)):
            # and lay them out left to right, a {spacing} apart
            self.drawFactory(factory=factory, position=(index * self.spacing, 0, 0))
        # each factory drew a slot for every one of its traits; the products that factories
        # share become one slot each
        self.share()

        # initialize the set of products
        inputs = [product for product, _ in flow.pyre_inputs()]
        outputs = [product for product, _ in flow.pyre_outputs()]
        # show me the products the flow connects, when someone is listening
        channel = journal.debug("qed.ux.diagram")
        # the ones that come in
        channel.line(f"input:")
        # go through them
        for product in inputs:
            # and name each one
            channel.line(f"  {product}")
        # the ones that go out
        channel.line(f"output:")
        # go through them
        for product in outputs:
            # and name each one
            channel.line(f"  {product}")
        # flush
        channel.log()

        # all done
        return flow

    def share(self):
        """
        Merge the slots whose traits are bound to the same product into one slot that carries
        the product, on the side of the factory that makes it, so the diagram shows the data
        moving from its maker to its users
        """
        # the slots of each product, by product identity, since flow nodes need not be hashable
        groups = {}
        # go through my slots, in a stable order
        for slot in sorted(self.slots, key=lambda slot: slot.position):
            # find the product its traits are bound to
            product = self.product(slot=slot)
            # a slot whose traits are bound to nothing
            if product is None:
                # has nothing to share
                continue
            # otherwise, file it with the other slots of its product
            groups.setdefault(id(product), (product, []))[1].append(slot)
        # go through the products
        for product, slots in groups.values():
            # a product that only one slot knows about is not shared
            if len(slots) < 2:
                # so leave it alone
                continue
            # the slot that stays is the one its maker writes, if there is one
            keeper = next((slot for slot in slots if slot.writers), slots[0])
            # it carries the product
            keeper.product = product
            # and its label, which names the product
            labels = keeper.labels
            # add them to my pile of labels
            self.labels |= labels
            # and my index
            self.nodes.update((label.eid, label) for label in labels)
            # go through the other slots
            for dead in slots:
                # skipping the one that stays
                if dead is keeper:
                    # on to the next
                    continue
                # take the slot out of my slot index
                self.slots.discard(dead)
                # and my node index
                del self.nodes[dead.eid]
                # and out of the layout, if it holds the spot
                if self.layout.get(dead.position) is dead:
                    # by removing it
                    del self.layout[dead.position]
                # the slot that stays takes over its connections
                _, deltaLabels, _ = keeper.merge(other=dead)
                # the labels the merge made obsolete
                _, obsolete, _ = deltaLabels
                # go through them
                for label in obsolete:
                    # and forget each one
                    self.labels.discard(label)
                    # in both places
                    self.nodes.pop(label.eid, None)
            # the connectors that now reach the slot that stays
            for connector in keeper.connections():
                # place their labels next to it
                connector.moved()
        # all done
        return

    def product(self, slot):
        """
        Find the product that the traits connected to {slot} are bound to, or nothing when they
        disagree or there are none
        """
        # the products, by identity
        products = {}
        # go through the connections of the slot
        for connector in slot.connections():
            # get the flow factory behind the diagram entity
            factory = connector.factory.factory
            # go through the traits of the connection
            for trait in connector:
                # look up the product bound to it
                product = factory.pyre_inventory[trait].value
                # and if there is one
                if product is not None:
                    # remember it
                    products[id(product)] = product
        # a slot whose traits agree on one product carries it
        if len(products) == 1:
            # so hand it off
            return next(iter(products.values()))
        # otherwise, there is nothing to say
        return None

    def order(self, flow):
        """
        Sort the factories of {flow} so that each one comes after the factories that make its
        inputs, keeping the order the flow lists them in wherever the data does not decide
        """
        # the factories, in the order the flow lists them
        pending = list(flow.pyre_factories())
        # the factories that make each product, by product identity, since flow nodes need not
        # be hashable
        makers = {}
        # go through the factories
        for factory in pending:
            # and their outputs
            for product, _ in factory.pyre_outputs():
                # an unbound output makes nothing
                if product is not None:
                    # otherwise, record its maker
                    makers.setdefault(id(product), []).append(factory)
        # the factories each one waits for, by identity: the makers of its inputs, other than
        # itself
        upstream = {
            id(factory): {
                id(maker)
                for product, _ in factory.pyre_inputs()
                if product is not None
                for maker in makers.get(id(product), [])
                if maker is not factory
            }
            for factory in pending
        }
        # the factories in flow order
        ordered = []
        # and the identities of the ones that have their places
        placed = set()
        # until every factory has a place
        while pending:
            # the first one whose upstream factories all have their places goes next; a cycle
            # leaves none, and then the first one in line breaks it
            ready = next(
                (factory for factory in pending if upstream[id(factory)] <= placed),
                pending[0],
            )
            # place it
            ordered.append(ready)
            # remember that it has its place
            placed.add(id(ready))
            # and take it out of line
            pending.remove(ready)
        # hand off the order
        return ordered

    def drawFactory(self, factory, position):
        """
        Add {factory} to the diagram
        """
        # build an entity
        entity = Factory(factory=factory, position=position)
        # grab its slots
        slots = entity.slots
        # and its connectors
        connectors = list(entity.connections())
        # make a pile of labels
        labels = []
        # add the entity labels
        labels.extend(entity.labels)
        # go through the connectors
        for connector in connectors:
            # and their labels to the pile
            labels.extend(connector.labels)

        # add the entity to the set of factories
        self.factories.add(entity)
        # its slots to the pile of slots
        self.slots |= slots
        # and its labels to the pile of labels
        self.labels |= set(labels)
        # update my node index: keep track of the new entity
        self.nodes[entity.eid] = entity
        # its slots
        self.nodes.update((slot.eid, slot) for slot in slots)
        # and the new labels
        self.nodes.update((label.eid, label) for label in labels)
        # update my layout by adding the factory
        self.layout[entity.position] = entity
        # and its slots
        self.layout.update((slot.position, slot) for slot in slots)
        # all done
        return entity, labels, slots, connectors

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
