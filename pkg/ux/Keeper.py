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
            # and file the section, along with the entries to remove; it is written whether
            # or not there is one already
            targets.setdefault(target, []).append((name, section, vacuous, False))
        # the views go to the workspace file
        for name, section in named.items():
            # whole
            targets.setdefault(self.workspace, []).append((name, section, (), False))
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

    def persistArchive(self, archive):
        """
        Write {archive} into the configuration files, at the request of the user: its section,
        with whatever the session assigned to it, and its entry in the list that attaches it
        at boot. Nothing else is written: the other archives of the session are their own
        business
        """
        # an archive has no parts worth describing separately
        return self._persistEntity(entity=archive, parts=(), roster=self.archiveRoster)

    def persistReader(self, reader):
        """
        Write {reader} into the configuration files, at the request of the user: that it is
        part of the workspace, and nothing about how it was being looked at

        That means its entry in the list that attaches it at boot and, if it does not have one
        already, a section that says what it is: its product, what the session had to be told
        in order to make it, and how to get at the product. A reader that came from a file has
        a section, written the way the user wanted it, and that is left alone. The state of
        its controllers is not part of what a reader is; the control panels save that
        """
        # how to get at the product: what its archive says about getting in, and its own
        # settings; safe to write down, unlike the keys they lead to
        access = reader.access() if hasattr(reader, "access") else {}
        # write
        return self._persistEntity(
            entity=reader,
            parts=(),
            roster=self.readerRoster,
            extras={"credentials": access} if access else {},
            create=True,
        )

    def forgetArchive(self, archive):
        """
        Remove {archive} from the configuration of the workspace, because the user disconnected
        it: its entry in the list that attaches it at boot goes, and so does its section, when
        that lives in the workspace file. A section in any other file stays: it is inert
        without the entry, and other workspaces may still depend on it
        """
        # delegate
        return self._forgetEntity(entity=archive, roster=self.archiveRoster)

    def forgetReader(self, reader):
        """
        Remove {reader} from the configuration of the workspace, because the user disconnected
        it; the rules are the ones for archives
        """
        # delegate
        return self._forgetEntity(entity=reader, roster=self.readerRoster)

    def forgetFolders(self, archive, folders):
        """
        Remove {folders} from the record of what {archive} has on display, because they are no
        longer there. This corrects what was saved and records nothing new: the rest of the
        record, and the rest of the session, are left alone
        """
        # describe the archive, to find out where it lives
        recipe = pyre.config.newRecipe()
        recipe.add(archive)
        # its name
        name = archive.pyre_name
        # the file it came from, or the workspace file
        target = self._origin(component=archive) or self.workspace

        # the edit
        def prune(editor):
            # look for the section of the archive
            section = editor.find(name)
            # an archive that was never saved has no record to correct
            if section is None or editor.get(*section, "expanded") is None:
                # so there is nothing to do
                return
            # go through the folders
            for folder in folders:
                # and take each one out of the record
                editor.remove(*section, "expanded", value=folder)
            # a record with nothing left in it
            if not editor.get(*section, "expanded"):
                # says what its absence would
                editor.delete(*section, "expanded")
            # all done
            return

        # apply it to the file with the section
        return self._write(targets={target: []}, lists={}, amend=prune, where=target)

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

    @staticmethod
    def _spelled(section, owner):
        """
        Respell the values of {section} that refer to components the framework built under
        names of its own choosing, e.g. the datatype that binds the cell of a reader

        Such a name means nothing in a later session, and nobody would write it by hand. The
        family of the component says everything there is to say, and resolves into a fresh
        instance at boot. References to {owner} and its parts are names that were chosen, and
        they stay
        """
        # make a pile
        spelled = {}
        # go through the settings
        for trait, value in section.items():
            # a reference to a component is a family and a name
            if isinstance(value, str) and "#" in value:
                # take it apart
                family, _, name = value.partition("#")
                # a family is a dotted name; anything else with a '#' in it, e.g. a uri with
                # a fragment, is not a reference
                if not all(part.isidentifier() for part in family.split(".")):
                    # so it stays as it is
                    spelled[trait] = value
                    # and on to the next one
                    continue
                # a name that was not derived from the owner was generated
                if name != owner and not name.startswith(f"{owner}."):
                    # so the family is all that is worth keeping
                    value = family
            # record
            spelled[trait] = value
        # hand off the pile
        return spelled

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

    def _write(self, targets, lists, amend=None, where=None):
        """
        Edit the files in {targets} with their sections, and the workspace file with the
        plexus {lists}; {amend}, when given, is an edit to apply to the file at {where}, the
        workspace file by default
        """
        # the workspace file always gets the lists
        targets.setdefault(self.workspace, [])
        # the file that gets the extra edit
        where = self.workspace if where is None else where
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
            for name, section, vacuous, create in sections:
                # look for the entry that configures the component
                found = editor.find(name)
                # if it is there, and this section is only for components that have none
                if create and found is not None:
                    # the user's spelling stands
                    continue
                # otherwise, use it, or make a section for the component
                keys = found or (name,)
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
            # the extra edit
            if amend is not None and path == where:
                # goes to its file
                amend(editor)
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

    @property
    def archiveRoster(self):
        """
        The list that attaches the archives: its name, what boot attached, what is connected
        """
        # pack it
        return "archives", self.store.bootArchives, self.store.archives

    @property
    def readerRoster(self):
        """
        The list that attaches the readers: its name, what boot attached, what is connected
        """
        # pack it
        return "datasets", self.store.bootSources, self.store.sources

    def _persistEntity(self, entity, parts, roster, extras=None, create=False):
        """
        Write {entity}, a component that one of the plexus lists attaches at boot, along with
        its {parts}, and make sure the list described by {roster} names it; {extras} are
        settings to add to the section of the entity that are not among its assigned traits.
        With {create}, the section of the entity is written only when it does not have one
        """
        # describe the entity and its parts
        recipe = pyre.config.newRecipe()
        recipe.add(entity)
        # go through the parts
        for part in parts:
            # and describe each one
            recipe.add(part)
        # the name of the entity, and the way the list spells it
        name = entity.pyre_name
        spec = recipe.spec(name)
        # the sections to write, keyed by the file they go to
        targets = {}
        # go through what was described
        for key, section in recipe.sections.items():
            # the entity and its parts are named after it; anything else, e.g. a component
            # the framework built under a generated name, is rebuilt at boot
            if key != name and not key.startswith(f"{name}."):
                # so it is not worth keeping
                continue
            # get the component
            component = recipe.components[key]
            # keep only what the session assigned
            section = self._assigned(component=component, section=section)
            # spell the components it refers to the way a person would
            section = self._spelled(section=section, owner=name)
            # the entity itself gets the extras
            if key == name and extras:
                # which win over whatever is there
                section.update(extras)
            # of those, find the ones that say nothing, and whose entries should go
            vacuous = self._vacuous(component=component, section=section)
            # a section with nothing to say
            if not section:
                # says nothing
                continue
            # find the file the component came from, or fall back to the workspace file
            target = self._origin(component=component) or self.workspace
            # and file the section, along with the entries to remove, and whether an existing
            # section is to be left alone
            targets.setdefault(target, []).append((key, section, vacuous, create))

        # the list that attaches the entity lives in the workspace file
        def attach(editor):
            # get the list, making it if this is the first time anything is saved
            keys, entries = self._roster(editor=editor, roster=roster)
            # if the entity is not there yet
            if name not in [self._named(entry) for entry in entries]:
                # add it
                entries.append(spec)
            # and store the list
            editor.set(*keys, value=entries)
            # all done
            return

        # write everything
        return self._write(targets=targets, lists={}, amend=attach)

    def _forgetEntity(self, entity, roster):
        """
        Take {entity} out of the list described by {roster}, and remove its section when that
        lives in the workspace file
        """
        # the name of the entity
        name = entity.pyre_name
        # what boot attached
        _, boot, _ = roster

        # the edit
        def detach(editor):
            # look for the list, without making one
            keys = self._rosterKeys(editor=editor, roster=roster)
            # if there is no list, and the entity was not attached at boot
            if keys is None and name not in boot:
                # the files know nothing about it, so there is nothing to forget
                return
            # otherwise get the list, making it if necessary: an entity that was attached
            # by default stays away only if there is a list that leaves it out
            keys, entries = self._roster(editor=editor, roster=roster)
            # leave the entity out, and store the list
            editor.set(*keys, value=[e for e in entries if self._named(e) != name])
            # look for the section of the entity, wherever the scoping of this file put it
            section = editor.find(name)
            # if it is here
            if section is not None:
                # it goes
                editor.delete(*section)
            # go through the top level sections that are left
            for key in list(editor.document.keys()):
                # the name each one spells
                spelled = self._named(key)
                # the section of the entity, and the sections of its parts
                if spelled == name or spelled.startswith(f"{name}."):
                    # go as well
                    editor.delete(key)
            # all done
            return

        # apply it to the workspace file
        return self._write(targets={}, lists={}, amend=detach)

    def _rosterKeys(self, editor, roster):
        """
        Find the list described by {roster} in the document {editor} holds, if it has one
        """
        # the name of the list
        trait, _, _ = roster
        # the entry may be a top level key, the way pyre aliases plexus traits, or sit
        # within the plexus section
        return editor.find(trait) or editor.find(f"{self.plexus.pyre_name}.{trait}")

    def _roster(self, editor, roster):
        """
        Get the list described by {roster} from the document {editor} holds, along with where
        it lives; when the document has none, make the list that reproduces what happens
        without one

        A list in the workspace file replaces whatever would have been attached without it:
        the entities named by another configuration file, or the ones the application attaches
        by default, such as the archive over the current directory. So the first list to be
        written names what was attached at boot and is still connected; that way, making the
        list changes nothing the user did not ask to change
        """
        # unpack
        trait, boot, connected = roster
        # look for the list
        keys = self._rosterKeys(editor=editor, roster=roster)
        # if it is there
        if keys is not None:
            # hand off a copy of it
            return keys, [str(entry) for entry in editor.get(*keys) or []]
        # otherwise, describe what was attached at boot and is still around
        recipe = pyre.config.newRecipe()
        # make a pile
        entries = []
        # go through what is connected
        for entity in connected:
            # whatever the session made is not part of what boot would attach
            if entity.pyre_name not in boot:
                # so it stays out
                continue
            # describe the rest
            recipe.add(entity)
            # and add them to the pile, the way the list spells them
            entries.append(recipe.spec(entity.pyre_name))
        # the list goes at the top level, the way pyre aliases plexus traits
        return (trait,), entries

    @staticmethod
    def _named(entry):
        """
        Extract the name of the component that {entry}, a specification from a list, builds
        """
        # the name follows the family
        return str(entry).split("#")[-1]

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
