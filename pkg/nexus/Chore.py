# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre
import qed


# the shared core of the units of work handed to the crews
class Chore(pyre.nexus.task):
    """
    The common machinery of qed crew tasks

    Chores are picklable descriptions of work built on the team side by harvesting live
    component state, and executed on the worker side, where they rebuild the reader from
    its recipe so each crew member owns its file handles; this base class contributes the
    recipe harvest, the worker-side reader reconstruction, and the identity freezing that
    lets equal tasks share a single execution
    """

    # metamethods
    def __hash__(self):
        # my identity is my specification
        return hash(self.identity)

    def __eq__(self, other):
        # two chores are the same work when their full specifications agree
        return type(other) is type(self) and other.identity == self.identity

    # implementation details - team side
    def _harvestReader(self, reader):
        """
        Build the recipe that lets a worker reconstruct {reader} with its own file handles
        """
        # initialize the recipe
        config = {}
        # go through the reader properties
        for trait in reader.pyre_properties():
            # get the name
            name = trait.name
            # the dataset pile is derived state; workers rebuild it from the file
            if name == "datasets":
                # so leave it behind
                continue
            # get the value
            value = getattr(reader, name)
            # trivial settings contribute nothing
            if value is None:
                # so skip them
                continue
            # a list of components, e.g. the members of a stack, travels as recipes
            if isinstance(value, (list, tuple)) and all(
                hasattr(item, "pyre_family") for item in value
            ):
                # each member contributes its factory and its own recipe
                config[name] = tuple(
                    (item.pyre_family(), self._harvestReader(reader=item)) for item in value
                )
                # on to the next trait
                continue
            # everything else travels in wire-friendly form
            config[name] = self._scrub(value=value)
        # go through the reader facilities
        for trait in reader.pyre_facilities():
            # get the name
            name = trait.name
            # the selector table is derived from the file contents
            if name == "selectors":
                # so leave it behind
                continue
            # get the bound component
            value = getattr(reader, name)
            # unbound facilities contribute nothing
            if value is None:
                # so skip them
                continue
            # bound ones, e.g. the cell type of flat readers, travel as their family name
            config[name] = value.pyre_family()
        # archive-backed readers retain access credentials, which are not traits; a worker
        # cannot reach the archive, but it can present the credentials
        credentials = getattr(reader, "credentials", None)
        # if there are any
        if credentials:
            # add them to the recipe
            config["credentials"] = dict(credentials)
        # hand off the recipe
        return config

    def _harvestComponent(self, component):
        """
        Capture the configuration tree of {component} as a nest of plain dictionaries
        """
        # initialize the pile
        config = {}
        # components may declare traits that shape the presentation but not the rendered
        # pixels, e.g. the display bounds of controllers; they are left out, so adjusting
        # them neither perturbs the tile identity nor invalidates cached work
        cosmetic = getattr(component, "cosmetic", ())
        # go through the properties
        for trait in component.pyre_properties():
            # skip the presentation-only ones
            if trait.name in cosmetic:
                # they do not travel
                continue
            # reduce each value to wire-friendly form, insisting on primitives so that
            # infrastructure state, e.g. the flow bookkeeping sets, gets left behind
            value = self._scrub(value=getattr(component, trait.name), strict=True)
            # if the value survived
            if value is not self._opaque:
                # record it
                config[trait.name] = value
        # go through the facilities, e.g. the controllers of a channel pipeline
        for trait in component.pyre_facilities():
            # and capture each part recursively
            config[trait.name] = self._harvestComponent(component=getattr(component, trait.name))
        # hand off the pile
        return config

    def _scrub(self, value, strict=False):
        """
        Reduce {value} to a form that can be pickled and re-cast by a trait on arrival
        """
        # primitives travel as they are
        if value is None or isinstance(value, (bool, int, float, str)):
            # untouched
            return value
        # sequences travel member by member
        if isinstance(value, (tuple, list)):
            # reduce the members
            members = tuple(self._scrub(value=item, strict=strict) for item in value)
            # a sequence with an opaque member is itself opaque
            return self._opaque if self._opaque in members else members
        # tables travel entry by entry
        if isinstance(value, dict):
            # reduce the entries
            entries = {key: self._scrub(value=item, strict=strict) for key, item in value.items()}
            # a table with an opaque entry is itself opaque
            return self._opaque if self._opaque in entries.values() else entries
        # in strict mode, nothing else makes the cut
        if strict:
            # so mark it
            return self._opaque
        # otherwise, e.g. for the uris in reader recipes, fall back to the string form
        return str(value)

    def _freeze(self, value):
        """
        Reduce {value} to a hashable form, so specifications can be compared
        """
        # tables freeze entry by entry, in a canonical order
        if isinstance(value, dict):
            # as sorted tuples of frozen pairs
            return tuple((key, self._freeze(value=item)) for key, item in sorted(value.items()))
        # sequences freeze member by member
        if isinstance(value, (tuple, list)):
            # in a tuple
            return tuple(self._freeze(value=item) for item in value)
        # everything else is already a hashable primitive
        return value

    # the marker for values that cannot travel
    _opaque = object()

    # implementation details - worker side
    def _locateReader(self, readers, measure=True):
        """
        Retrieve my reader from the {readers} registry, building it on first contact

        {measure} says whether the datasets should sample themselves as they are
        discovered: a survey wants the numbers, since they are its deliverable, while a
        render is about to install the client's controller state over anything they would
        produce, and paying for a sample it discards is pure waste
        """
        # if my reader is already in the registry
        if self.reader in readers:
            # use it
            return readers[self.reader]
        # otherwise, resolve my factory
        factory = qed.protocols.reader.pyre_resolveSpecification(spec=self.factory)
        # work on a copy of the recipe, since member recipes get materialized in place
        config = dict(self.config)
        # go through the settings
        for name, value in config.items():
            # looking for member recipes, e.g. the readers of a stack
            if (
                isinstance(value, tuple)
                and value
                and all(isinstance(item, tuple) and len(item) == 2 for item in value)
                and all(isinstance(item[0], str) and isinstance(item[1], dict) for item in value)
            ):
                # resurrect each member with its own file handles
                config[name] = [
                    qed.protocols.reader.pyre_resolveSpecification(spec=family)(
                        name=f"{self.reader}.crew.{index}", **recipe
                    )
                    for index, (family, recipe) in enumerate(value)
                ]
        # build a fresh instance so this process owns its file handles; the derived name
        # avoids clashing with the team side instance this process may have inherited
        reader = factory(name=f"{self.reader}.crew", **config)
        # construction is passive; a worker exists to touch the data, so make first
        # contact now
        reader.open(measure=measure)
        # register it
        readers[self.reader] = reader
        # and hand it off
        return reader

    def _locateDataset(self, reader):
        """
        Find the dataset of {reader} that matches my selector
        """
        # go through the reader datasets
        for dataset in reader.datasets:
            # looking for the one whose selector matches mine
            if dict(dataset.selector) == self.selector:
                # hand it off
                return dataset
        # not finding one means the reconstruction diverged from the team side view
        raise self.RecoverableError(description=f"no dataset matches the selector {self.selector}")

    def _configure(self, component, config):
        """
        Mirror the {config} tree harvested on the team side onto {component}
        """
        # go through the component properties
        for trait in component.pyre_properties():
            # get the name
            name = trait.name
            # if the configuration has an opinion
            if name in config:
                # apply it; the trait casts the wire form back into its native type
                setattr(component, name, config[name])
        # go through the facilities
        for trait in component.pyre_facilities():
            # get the name
            name = trait.name
            # if the configuration has an opinion
            if name in config:
                # descend into the part
                self._configure(component=getattr(component, name), config=config[name])
        # hand back the configured component
        return component


# end of file
