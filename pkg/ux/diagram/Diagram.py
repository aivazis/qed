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
    spacing.default = 10
    spacing.doc = (
        "the distance between neighboring factories; at 10, the outputs of a factory and the"
        " inputs of its neighbor share their homes, so the slots that bind them stay put"
    )

    # public data
    @property
    def relay(self):
        """
        My {relay} id, by which clients address me
        """
        # splice together my {family} and {name}
        return f"{self.pyre_family()}:{self.pyre_name}.diagram"

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
            channel.line(f"in the diagram {self.relay}")
            channel.log(f"node '{eid}' not found")
            # in case firewalls aren't fatal, return the found node
            return node

        # make sure it's the right type
        if node.typename() != typename:
            # if not, we have a problem that's almost certainly a bug
            channel = journal.firewall("qed.ux.diagram.nodes")
            # so complain
            channel.line(f"while looking up '{relay}'")
            channel.line(f"in the diagram {self.relay}")
            channel.log(f"type mismatch: retrieved node is '{typename}'")
            # in case firewalls aren't fatal, return the found node
            return node

        # all done
        return node

    # new nodes
    def addFactory(self, position, protocol=None, pin=None):
        """
        Add a factory that satisfies {protocol} to the recipe, optionally pinned to a class or an
        instance, and draw it at {position}
        """
        # add the factory to the recipe, named after what it is
        node = self.recipe.factory(
            name=self.recipe.vacant(name=Factory.describe(protocol=protocol, pin=pin)),
            protocol=protocol,
            pin=pin,
        )
        # and draw it
        return self.drawFactory(node=node, position=position)

    def moveGroup(self, nodes, anchor, position):
        """
        Move {nodes}, along with the slots that connect only to the factories among them, so that
        {anchor} lands at {position} and the rest keep their places around it; the move is all or
        nothing, and never merges: it is refused if any member would land on a node outside the
        group
        """
        # the group: the nodes, and the slots their factories take along
        group = list(nodes) + [slot for slot in self.cohort(nodes=nodes) if slot not in nodes]
        # how far the group moves
        delta = tuple(p - q for p, q in zip(position, anchor.position))
        # where each member is headed
        targets = [(node, tuple(p + d for p, d in zip(node.position, delta))) for node in group]
        # the members, by identity
        members = {id(node) for node in group}
        # if any of them would land on somebody else
        for _, target in targets:
            # find out who is there
            other = self.layout.get(target)
            # if it is not one of us
            if other is not None and id(other) not in members:
                # the move is refused
                return False
        # a member in the middle of a move of its own is no longer moving
        if id(self.migrant) in members:
            # so forget it
            self.migrant = None
        # the members leave their spots, all of them before any of them lands
        for node, _ in targets:
            # if the node holds its spot
            if self.layout.get(node.position) is node:
                # release it
                del self.layout[node.position]
        # then they move, and take their new spots
        for node, target in targets:
            # move the node, along with its labels
            node.move(position=target)
            # and take the spot
            self.layout[target] = node
        # all done
        return True

    def cohort(self, nodes):
        """
        The slots that a move of {nodes} takes along: the ones every connection of which leads to
        a factory among them, which includes the own unbound slots of each factory and the
        bindings among them
        """
        # the factories among the nodes, by identity
        factories = {id(node) for node in nodes if node in self.factories}
        # the slots
        cohort = []
        # go through my slots, in a stable order
        for slot in sorted(self.slots, key=lambda slot: slot.position):
            # the factories the slot connects to
            owners = {id(connector.factory) for connector in slot.connections()}
            # if it connects to some, and only to factories among the nodes
            if owners and owners <= factories:
                # it comes along
                cohort.append(slot)
        # hand them off
        return cohort

    def followers(self, node):
        """
        The slots that go wherever {node} goes: a factory's own unbound slots, the ones no other
        factory connects to; other nodes have none
        """
        # only factories have followers
        if not isinstance(node, Factory):
            # so there are none
            return []
        # its slots that only it connects to and that carry no product
        return [
            slot
            for slot in node.slots
            if slot.product is None and set(slot.readers) | set(slot.writers) == {node}
        ]

    def split(self, slot):
        """
        Undo the binding {slot} stands for: every trait connected to it gets an unbound slot of its
        own, at its home or nearby; a slot that is already one trait's own, unbound slot has
        nothing to undo
        """
        # the connections of the slot, with their direction
        connections = [(factory, connector, True) for factory, connector in slot.readers.items()]
        connections += [(factory, connector, False) for factory, connector in slot.writers.items()]
        # the traits connected to it, one entry each, with their factory and direction
        traits = [
            (factory, trait, reads)
            for factory, connector, reads in connections
            for trait in list(connector)
        ]
        # a slot that is one trait's own, and carries no product
        if len(traits) <= 1 and slot.product is None:
            # has nothing to undo
            return False
        # a slot in the middle of a move is no longer moving
        if self.migrant is slot:
            # so forget it
            self.migrant = None
        # the traits are no longer bound to anything
        for factory, trait, _ in traits:
            # so undo their bindings in the recipe
            self.recipe.unbind(factory=factory.node.name, slot=trait.name)
        # and the product they shared goes, since no slot stands for it any more
        if slot.product is not None:
            # out of the recipe
            self.recipe.remove(name=slot.product.name)
        # forget the labels of its connectors
        for _, connector, _ in connections:
            # one connector at a time
            self.forget(nodes=connector.labels)
        # and the slot itself, along with its labels
        self.forget(nodes=slot.labels)
        self.forget(nodes=[slot])
        # the factories no longer use the slot
        for factory, _, _ in connections:
            # so drop it from their piles
            factory.slots.discard(slot)
        # where each trait would like its slot
        homes = [factory.home(trait) for factory, trait, _ in traits]
        # a carefully packed diagram may have the bound slot right where several of the traits
        # call home; each of those steps half a cell toward its own factory, so the binding comes
        # apart along its own line instead of piling up on one spot
        claims = {}
        # count the claims on each spot
        for home in homes:
            # one at a time
            claims[home] = claims.get(home, 0) + 1
        # go through the traits
        for (factory, trait, reads), home in zip(traits, homes):
            # a spot claimed by more than one trait
            if claims[home] > 1:
                # gives way to a step toward the factory
                home = self.toward(spot=home, factory=factory)
            # make the slot, at the spot or the nearest free one
            fresh = Slot(product=None, position=self.vacancy(spot=home))
            # connected the way it was
            if reads:
                # as an input
                fresh.connectReader(factory=factory, trait=trait)
            # or
            else:
                # as an output
                fresh.connectWriter(factory=factory, trait=trait)
            # which the factory uses from now on
            factory.slots.add(fresh)
            # and the diagram knows about
            self.adopt(slot=fresh)
        # all done
        return True

    def toward(self, spot, factory):
        """
        The spot half a cell from {spot} in the direction of {factory}: across, when they are in
        different columns, otherwise along the column
        """
        # unpack
        x, y, z = spot
        fx, fy, _ = factory.position
        # if they are in different columns
        if fx != x:
            # step across
            return (x + (1 if fx > x else -1), y, z)
        # otherwise, step along the column
        return (x, y + (1 if fy > y else -1), z)

    def adopt(self, slot):
        """
        Add a new {slot} to my indices, my layout, and my piles, along with the labels of its
        connectors
        """
        # the labels of its connectors
        labels = [label for connector in slot.connections() for label in connector.labels]
        # the slot
        self.slots.add(slot)
        self.nodes[slot.eid] = slot
        self.layout[slot.position] = slot
        # and the labels
        self.labels |= set(labels)
        self.nodes.update((label.eid, label) for label in labels)
        # all done
        return

    def vacancy(self, spot):
        """
        The free spot nearest {spot} along its column, trying {spot} first
        """
        # unpack
        x, y, z = spot
        # walk away from it, a cell at a time, alternating sides
        for step in range(64):
            # the offset of this attempt: 0, +2, -2, +4, -4, ...
            offset = 2 * ((step + 1) // 2) * (1 if step % 2 else -1)
            # the candidate
            candidate = (x, y + offset, z)
            # if it is free
            if candidate not in self.layout:
                # it will do
                return candidate
        # if nothing is free nearby, settle for the spot itself
        return spot

    def fits(self, position, protocol=None, pin=None):
        """
        Check whether a factory that satisfies {protocol}, optionally pinned, placed at
        {position} would land on free spots, along with all the slots it would bring
        """
        # a throwaway node, which no recipe knows about
        node = qed.flow.recipes.factory(name="", protocol=protocol, pin=pin)
        # and a throwaway entity, which places the slots of the factory around it
        entity = Factory(node=node, position=position)
        # the spots it would take
        spots = [entity.position] + [slot.position for slot in entity.slots]
        # it fits if none of them is taken
        return not any(spot in self.layout for spot in spots)

    def removeFactory(self, entity):
        """
        Remove the factory {entity} from the diagram and its recipe, along with its connectors
        and its bindings; the slots it leaves without any connections go as well, along with
        their products, the ones other factories still use stay
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
                # and its product, which the factory's removal leaves with no bindings
                if slot.product is not None:
                    # so the recipe forgets it too
                    self.recipe.remove(name=slot.product.name)
        # forget the labels of the factory
        self.forget(nodes=entity.labels)
        # and the factory itself
        self.forget(nodes=[entity])
        # take it out of the recipe, along with its bindings
        self.recipe.remove(name=entity.node.name)
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

    def addProduct(self, position, specification=None, pin=None):
        """
        Add a product that satisfies {specification} to the recipe, optionally pinned to a class
        or an instance, and draw it at {position}
        """
        # the name of the product: its specification, as far as it has one
        kind = "product" if specification is None else specification.__name__.lower()
        # add the product to the recipe
        product = self.recipe.product(
            name=self.recipe.vacant(name=kind), specification=specification, pin=pin
        )
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

        # a factory takes its own unbound slots along, so the figure keeps its shape
        followers = self.followers(node=node)
        # by as much as it moves
        delta = tuple(p - q for p, q in zip(position, node.position))
        # where each of them is headed
        targets = [(slot, tuple(p + d for p, d in zip(slot.position, delta))) for slot in followers]
        # the members of the group, which may land on each other's old spots
        group = {id(member) for member in [node, *followers]}
        # if any of them would land on somebody else
        for _, target in targets:
            # find out who is there
            other = self.layout.get(target)
            # if it is not one of us
            if other is not None and id(other) not in group:
                # the move is illegal
                return False

        # mark whether this move caused a collision
        self.collision = occupant

        # the followers leave their spots, all of them before any of them lands
        for slot, _ in targets:
            # if the slot holds its spot
            if self.layout.get(slot.position) is slot:
                # release it
                del self.layout[slot.position]
        # then they move, and take their new spots
        for slot, target in targets:
            # move the slot, along with its labels
            slot.move(position=target)
            # and take the spot
            self.layout[target] = slot

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
        delta = node.merge(other=dead)
        # and make the recipe agree with the slot that stays
        self.bind(slot=node)
        # hand off the changes
        return delta

    def bind(self, slot):
        """
        Make the recipe agree with {slot}: every trait connected to it is bound to its product,
        which is made when the slot stands for none yet; a slot that is one trait's own, unbound
        slot binds nothing
        """
        # the traits connected to the slot, with the recipe names of their factories
        traits = [
            (connector.factory.node.name, trait)
            for connector in slot.connections()
            for trait in connector
        ]
        # a slot that is one trait's own and stands for no product
        if len(traits) < 2 and slot.product is None:
            # binds nothing
            return
        # a slot that stands for no product yet
        if slot.product is None:
            # what the most demanding of its traits expects
            spec = self.refined(specs=[trait.protocol for _, trait in traits])
            # becomes the specification of a new product, named after it
            product = self.recipe.product(
                name=self.recipe.vacant(name=spec.__name__.lower()), specification=spec
            )
            # which the slot stands for from now on
            self.attach(slot=slot, product=product)
        # the name of the product
        name = slot.product.name
        # go through the traits
        for factory, trait in traits:
            # a trait that is bound to the product already
            if self.recipe.binding(factory=factory, slot=trait.name) == (factory, trait.name, name):
                # is left alone, so a live factory is not disturbed
                continue
            # the rest get bound to it
            self.recipe.bind(factory=factory, slot=trait.name, product=name)
        # all done
        return

    def attach(self, slot, product):
        """
        Make {slot}, which stands for no product and has no labels, stand for {product}, and
        give it the label that names it
        """
        # attach the product
        slot.product = product
        # the slot's labels are made the first time they are asked for; forget the ones made
        # before it had a product, which are none
        slot._labels = None
        # make the new ones
        labels = slot.labels
        # add them to my pile of labels
        self.labels |= labels
        # and my index
        self.nodes.update((label.eid, label) for label in labels)
        # all done
        return

    def refined(self, specs):
        """
        The most refined of the specifications in {specs}
        """
        # the most refined so far
        refined = None
        # go through them
        for spec in specs:
            # one that refines the best so far
            if refined is None or issubclass(spec, refined):
                # takes over
                refined = spec
        # hand it off
        return refined

    # metamethods
    def __init__(self, recipe=None, editable=True, **kwds):
        # chain up
        super().__init__(**kwds)
        # whether my structure can change: factories added or removed, slots bound or split
        self.editable = editable
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
        # set up my recipe
        self.recipe = self.draw(recipe=recipe)
        # all done
        return

    # implementation details
    def draw(self, recipe):
        """
        Lay out the factories of {recipe} and the products they share
        """
        # if there is no {recipe}
        if recipe is None:
            # make an empty one and return it
            return qed.flow.recipe()

        # otherwise, go through its factories in the order the data flows through them
        for index, node in enumerate(self.order(recipe=recipe)):
            # and lay them out left to right, a {spacing} apart
            self.drawFactory(node=node, position=(index * self.spacing, 0, 0))
        # each factory drew a slot for every one of its traits; the traits bound to the same
        # product share one slot
        self.share(recipe=recipe)

        # show me the products of the recipe, when someone is listening
        channel = journal.debug("qed.ux.diagram")
        # the ones that come in: nobody makes them
        channel.line(f"input:")
        # go through them
        for product in recipe.products():
            # the ones with no writers
            if not recipe.writers(product=product.name):
                # are named
                channel.line(f"  {product}")
        # the ones that go out: nobody uses them
        channel.line(f"output:")
        # go through them
        for product in recipe.products():
            # the ones with no readers
            if not recipe.readers(product=product.name):
                # are named
                channel.line(f"  {product}")
        # flush
        channel.log()

        # all done
        return recipe

    def share(self, recipe):
        """
        Give each product of {recipe} one slot, merging the slots whose traits are bound to it
        into the one on the side of the factory that makes it, so the diagram shows the data
        moving from its maker to its users
        """
        # the slots of each product, by name
        groups = {}
        # go through my slots, in a stable order
        for slot in sorted(self.slots, key=lambda slot: slot.position):
            # find the product its traits are bound to
            product = self.product(recipe=recipe, slot=slot)
            # a slot whose traits are bound to nothing
            if product is None:
                # has nothing to share
                continue
            # otherwise, file it with the other slots of its product
            groups.setdefault(product.name, (product, []))[1].append(slot)
        # go through the products
        for product, slots in groups.values():
            # the slot that stays is the one its maker writes, if there is one
            keeper = next((slot for slot in slots if slot.writers), slots[0])
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
            # the slot that stays now has all the connections, so it can stand for the product
            # and get the label that names it
            self.attach(slot=keeper, product=product)
            # the connectors that now reach the slot that stays
            for connector in keeper.connections():
                # place their labels next to it
                connector.moved()
        # all done
        return

    def product(self, recipe, slot):
        """
        Find the product of {recipe} that the traits connected to {slot} are bound to, or
        nothing when they disagree or there are none
        """
        # the names of the products
        names = set()
        # go through the connections of the slot
        for connector in slot.connections():
            # get the name of the factory behind the diagram entity
            factory = connector.factory.node.name
            # go through the traits of the connection
            for trait in connector:
                # look up the binding of the trait
                binding = recipe.binding(factory=factory, slot=trait.name)
                # and if there is one
                if binding is not None:
                    # remember its product
                    names.add(binding.product)
        # a slot whose traits agree on one product stands for it
        if len(names) == 1:
            # so hand it off
            return recipe.node(name=names.pop())
        # otherwise, there is nothing to say
        return None

    def order(self, recipe):
        """
        Sort the factories of {recipe} so that each one comes after the factories that make its
        inputs, keeping the order the recipe lists them in wherever the data does not decide
        """
        # the factories, in the order the recipe lists them
        pending = list(recipe.factories())
        # the factories each one waits for, by name: the makers of its inputs, other than itself
        upstream = {
            node.name: {
                writer.factory
                for reader in recipe.bindings
                if reader.factory == node.name and recipe.reads(binding=reader)
                for writer in recipe.writers(product=reader.product)
                if writer.factory != node.name
            }
            for node in pending
        }
        # the factories in flow order
        ordered = []
        # and the names of the ones that have their places
        placed = set()
        # until every factory has a place
        while pending:
            # the first one whose upstream factories all have their places goes next; a cycle
            # leaves none, and then the first one in line breaks it
            ready = next(
                (node for node in pending if upstream[node.name] <= placed),
                pending[0],
            )
            # place it
            ordered.append(ready)
            # remember that it has its place
            placed.add(ready.name)
            # and take it out of line
            pending.remove(ready)
        # hand off the order
        return ordered

    def drawFactory(self, node, position):
        """
        Draw the factory {node} of my recipe at {position}
        """
        # build an entity
        entity = Factory(node=node, position=position)
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
        # a diagram that cannot be edited
        if not self.editable:
            # binds nothing
            return False

        # if either is a factory
        if isinstance(n1, Factory) or isinstance(n2, Factory):
            # the binding is not supported
            return False

        # if both are products
        if n1.product is not None and n2.product is not None:
            # the binding is not supported
            return False

        # what the two slots must satisfy: what their traits expect
        specs = [trait.protocol for slot in (n1, n2) for c in slot.connections() for trait in c]
        # and what their products were declared with
        specs += [
            slot.product.specification
            for slot in (n1, n2)
            if slot.product is not None and slot.product.specification is not None
        ]
        # any two of them that are no refinement of each other, either way
        for index, one in enumerate(specs):
            # against the rest
            for other in specs[index + 1 :]:
                # cannot share a product
                if not (issubclass(one, other) or issubclass(other, one)):
                    # so the binding is not supported
                    return False

        # anything else is ok
        return True

    # debugging support
    def dump(self):
        """
        Generate a report with my slots and factories
        """
        # first my name
        yield f"diagram: {self.relay}"
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
