# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre
import qed
import journal


# the keeper of the configuration files
class Keeper:
    """
    The keeper of the user's configuration files: it writes the state of the store back into
    them, so that the next session starts where this one left off

    The files are edited in place, never regenerated. A component that came from a file has
    its section augmented there with whatever the session assigned to it; a component the
    session made gets a section in the workspace file, the one in the directory the user
    launched from, along with an entry in the plexus list that connects it at boot. Settings
    that came from a file and were not touched are left exactly as the user wrote them
    """

    # interface
    def persist(self, archives=True, sources=True, views=True):
        """
        Write the state of the store back into the configuration files; the flags say which
        parts of the state to write
        """
        # build the recipe of everything that persists
        recipe = pyre.config.newRecipe()
        # the connected archives
        connected = list(self.store.archives) if archives else []
        # go through them
        for archive in connected:
            # and describe each one
            recipe.add(archive)
        # the connected readers
        readers = list(self.store.sources) if sources else []
        # go through them
        for reader in readers:
            # describe each one
            recipe.add(reader)
            # along with the reference channels of its datasets, which hold the controller
            # ranges the views mirror
            for dataset in reader.datasets:
                # go through the channels
                for channel in dataset.channels.values():
                    # and describe each one
                    recipe.add(channel)
        # the views, under names that survive the session
        named, viewNames = self._views(recipe=recipe) if views else ({}, [])
        # the entities: the components the lists name, whose parts are named after them
        entities = [archive.pyre_name for archive in connected] + [
            reader.pyre_name for reader in readers
        ]
        # the sections to write, keyed by the file they go to
        targets = {}
        # go through the sections
        for name, section in recipe.sections.items():
            # a view was placed already
            if name in named:
                # so move on
                continue
            # get the component
            component = recipe.components[name]
            # keep only what the session assigned
            section = self._assigned(component=component, section=section)
            # of those, find the ones that say nothing, and whose entries should go
            vacuous = self._vacuous(component=component, section=section)
            # a section with nothing to say and nothing to take back
            if not section:
                # says nothing
                continue
            # a component that is neither an entity nor a part of one, e.g. a datatype the
            # framework built under a generated name to bind a reader's cell, is rebuilt at
            # boot from the entity that references it, so its section is not worth keeping
            if not any(name == entity or name.startswith(f"{entity}.") for entity in entities):
                # so move on
                continue
            # find the file the component came from, or fall back to the workspace file
            target = self._origin(component=component) or self.workspace
            # and file the section, along with the entries to remove
            targets.setdefault(target, []).append((name, section, vacuous))
        # the views go to the workspace file
        for name, section in named.items():
            # whole
            targets.setdefault(self.workspace, []).append((name, section, ()))
        # the plexus lists go to the workspace file as well
        lists = {}
        # the archives
        if archives:
            # by specification
            lists["archives"] = [recipe.spec(archive.pyre_name) for archive in connected]
        # the readers
        if sources:
            # by specification
            lists["datasets"] = [recipe.spec(reader.pyre_name) for reader in readers]
        # and the views
        if views:
            # by specification, under their session names
            lists["views"] = [f"{self.viewFamily}#{name}" for name in viewNames]
        # write everything
        written = self._write(targets=targets, lists=lists)
        # all done
        return written

    # metamethods
    def __init__(self, plexus, store, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the store
        self.store = store
        # and the plexus
        self.plexus = plexus
        # the workspace file, resolved so it matches the origins the file server reports
        self.workspace = pyre.primitives.path(plexus.workspace.path).resolve() / "qed.yaml"
        # the configuration files this session read, by the name pyre knows them by
        self.sources = self._sources()
        # all done
        return

    # implementation details
    def _views(self, recipe):
        """
        Describe the views of the viewports under names that survive the session
        """
        # make a pile
        named = {}
        # and a list of the views themselves
        viewNames = []
        # go through the viewports
        for index, viewport in enumerate(self.store.viewports):
            # get the view
            view = viewport.view()
            # a view without a reader shows nothing
            if view is None or view.reader is None:
                # so it is not worth keeping
                continue
            # the name the view carries in this session
            live = view.pyre_name
            # and the one it gets in the file
            name = f"view.{index}"
            # record it
            viewNames.append(name)
            # describe it, along with its parts
            recipe.add(view)
            # go through what was described
            for key in list(recipe.sections):
                # looking for the view and its parts
                if key != live and not key.startswith(f"{live}."):
                    # everything else stays
                    continue
                # take the section out of the recipe
                section = recipe.sections.pop(key)
                component = recipe.components[key]
                # keep what the session assigned; the view itself keeps everything, since it
                # is being written under a new name
                if key != live:
                    # so only the parts are filtered
                    section = self._assigned(component=component, section=section)
                # a part bound under the view's own name is the binding the framework makes
                # at boot, so its reference is not worth recording; the part's own section
                # carries what was assigned to it
                section = {
                    trait: value
                    for trait, value in section.items()
                    if not (isinstance(value, str) and value.endswith(f"#{live}.{trait}"))
                }
                # the view's channel is a per-view pipeline, so it is recorded by its tag,
                # which is how the view binds it at boot
                if key == live:
                    # get the channel
                    channel = view.channel
                    # if there is one
                    if channel is not None:
                        # record its tag
                        section["channel"] = channel.tag
                # a section with nothing to say
                if not section:
                    # says nothing
                    continue
                # rename it
                named[name + key[len(live) :]] = section
        # hand off the pile, and the names of the views
        return named, viewNames

    def _assigned(self, component, section):
        """
        Keep the entries of {section} that the session assigned to {component}, leaving out
        what came from a file and was not touched, so the file keeps the user's spelling
        """
        # get the inventory
        inventory = component.pyre_inventory
        # make a pile
        kept = {}
        # go through the section
        for name, value in section.items():
            # get the trait
            trait = component.pyre_trait(alias=name)
            # and the priority of its last assignment
            priority = inventory.getTraitPriority(trait=trait)
            # a value assigned by the session, at construction or later
            if priority is not None and priority.name in self.assigned:
                # is kept
                kept[name] = value
        # hand off the pile
        return kept

    def _vacuous(self, component, section):
        """
        Find the entries of {section} whose values say nothing that the absence of the entry
        would not: an empty collection for a trait of {component} whose default is empty

        A list that the session filled and then emptied was assigned, so it would be written,
        as a pair of brackets that tell the next session what it would have assumed anyway.
        The test is deliberately narrow: the values here are rendered for the file, and
        comparing those against the typed defaults of arbitrary traits invites false matches
        """
        # the kinds of value that can be empty
        collections = (list, tuple, set, dict)
        # make a pile
        vacuous = set()
        # go through the section
        for name, value in section.items():
            # anything but an empty collection
            if not isinstance(value, collections) or value:
                # has something to say
                continue
            # get the default of the trait
            default = component.pyre_trait(alias=name).default
            # if that is an empty collection as well
            if isinstance(default, collections) and not default:
                # the entry adds nothing
                vacuous.add(name)
        # hand off the pile
        return vacuous

    def _origin(self, component):
        """
        Find the file that configured {component}, if any
        """
        # get the inventory
        inventory = component.pyre_inventory
        # go through the traits
        for trait in component.pyre_configurables():
            # carefully, since a component may not track its provenance
            try:
                # get the provenance of the last assignment
                locator = inventory.getTraitLocator(trait=trait)
            # if it does not
            except (KeyError, AttributeError):
                # move on
                continue
            # walk the chain
            while locator is not None:
                # looking for a file
                source = getattr(locator, "source", None)
                # if this link names one this session read
                if source is not None and str(source) in self.sources:
                    # that is the origin
                    return self.sources[str(source)]
                # otherwise, follow the chain
                locator = getattr(locator, "next", None)
        # no file configured this component
        return None

    def _sources(self):
        """
        Map the configuration files this session read to their locations on disk
        """
        # make a pile
        sources = {}
        # get the file server
        fileserver = pyre.executive.fileserver
        # go through the sources the configurator loaded
        for uri, _ in pyre.executive.configurator.sources:
            # the name pyre knows the file by
            name = str(uri)
            # only yaml files can be edited
            if not name.endswith(".yaml"):
                # so skip the rest
                continue
            # carefully, since the file server may not be able to resolve it
            try:
                # find the file
                node = fileserver[pyre.primitives.uri.parse(name).address]
            # if it cannot
            except (KeyError, fileserver.NotFoundError, fileserver.FolderError):
                # skip it
                continue
            # record its location
            sources[name] = node.uri
        # hand off the pile
        return sources

    def _write(self, targets, lists):
        """
        Edit the files in {targets} with their sections, and the workspace file with the
        plexus {lists}
        """
        # the workspace file always gets the lists
        targets.setdefault(self.workspace, [])
        # the files written
        written = []
        # go through the targets
        for path, sections in targets.items():
            # carefully, since the file may not be editable
            try:
                # open the file
                editor = pyre.config.newYamlEditor(uri=path)
            # if the backend is missing
            except pyre.config.exceptions.MissingBackendError as error:
                # make a channel
                channel = journal.warning("qed.ux.persistence")
                # complain, once
                channel.line(f"cannot persist the session: {error}")
                # flush
                channel.log()
                # and give up on every file
                return written
            # go through the sections
            for name, section, vacuous in sections:
                # find the entry that configures the component, or make a section for it
                keys = editor.find(name) or (name,)
                # and go through the settings
                for trait, value in section.items():
                    # one that says nothing
                    if trait in vacuous:
                        # has its entry removed, if it has one; its absence says the same
                        editor.delete(*keys, trait)
                        # and that's all
                        continue
                    # the rest are stored in place
                    editor.set(*keys, trait, value=value)
            # the lists
            if path == self.workspace:
                # go through them
                for trait, specs in lists.items():
                    # and place each one
                    self._list(editor=editor, trait=trait, specs=specs)
            # carefully, since the file may not be writable
            try:
                # save
                editor.save()
            # if it is not
            except OSError as error:
                # make a channel
                channel = journal.warning("qed.ux.persistence")
                # complain
                channel.line(f"could not write '{path}'")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # and move on
                continue
            # record the file
            written.append(path)
        # all done
        return written

    def _list(self, editor, trait, specs):
        """
        Store {specs} as the plexus list {trait} in the document {editor} holds, dropping the
        sections of the views the list no longer names
        """
        # the entry may be a top level key, the way pyre aliases plexus traits, or sit
        # within the plexus section
        keys = editor.find(trait) or editor.find(f"{self.plexus.pyre_name}.{trait}") or (trait,)
        # the views the list named before
        if trait == "views":
            # get the old list
            old = editor.get(*keys) or []
            # the names it carried
            stale = {str(spec).split("#")[-1] for spec in old}
            # less the ones it still carries
            stale -= {str(spec).split("#")[-1] for spec in specs}
            # go through the top level keys of the document
            for key in list(editor.document.keys()):
                # the name each spells
                name = str(key).split("#")[-1]
                # sections of stale views and of their parts
                if any(name == item or name.startswith(f"{item}.") for item in stale):
                    # go
                    editor.delete(key)
        # store the list
        editor.set(*keys, value=list(specs))
        # all done
        return

    # constants
    # the priority categories of values the session assigned
    assigned = ("construction", "explicit", "persistent")
    # the family of the views
    viewFamily = "qed.ux.views.view"


# end of file
