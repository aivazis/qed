#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import importlib
import inspect
import json
import pkgutil
import sys

# support
import journal
import pyre
import qed


# the survey
class Readers(pyre.application, family="qed.etc.introspection.readers"):
    """
    Survey the reader classes of the installed qed: for every class that implements one of the
    reader protocols, the traits, methods and class-level attributes it has, and the class in its
    hierarchy that declares each one; the result is a list of rows, one per reader, written as
    json for the tables of the pyre::flow ledger
    """

    # user configurable state
    output = pyre.properties.path()
    output.default = "readers.json"
    output.doc = "the file that receives the survey"

    # the application entry point
    @pyre.export
    def main(self, *args, **kwds) -> int:
        """
        Survey the readers and write what was found
        """
        # load every module of the packages that hold readers
        self.load()
        # find the readers among the classes they define
        readers = self.readers()
        # what the framework puts on every component class and every flow factory
        framework = self.bookkeeping()
        # survey each reader, in the order of their families
        rows = [
            self.survey(cls=cls, framework=framework)
            for _, cls in sorted(readers.items(), key=lambda entry: entry[0])
        ]
        # go through them again
        for row in rows:
            # to name the readers that derive from each one
            row["derived"] = sorted(
                family
                for family, other in readers.items()
                if other is not readers[row["family"]] and issubclass(other, readers[row["family"]])
            )
            # which makes it a base for them
            row["base"] = bool(row["derived"])
        # write the survey
        with open(self.output, mode="w", encoding="utf-8") as stream:
            # as json
            json.dump(rows, stream, indent=1)
        # make a channel
        channel = journal.info("qed.introspection.readers")
        # and say what was done
        channel.log(f"surveyed {len(rows)} readers into '{self.output}'")
        # all done
        return 0

    # implementation details
    def load(self) -> None:
        """
        Import every module under the packages that hold readers, so their classes are defined
        """
        # the packages
        for package in (qed.readers, qed.stacks):
            # go through everything under each one
            for info in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
                # carefully
                try:
                    # import it
                    importlib.import_module(info.name)
                # a module whose optional externals are missing, such as gdal
                except ImportError as error:
                    # make a channel
                    channel = journal.warning("qed.introspection.readers")
                    # say it was left out, and why
                    channel.log(f"skipped '{info.name}': {error}")
        # all done
        return

    def readers(self) -> dict:
        """
        Find the classes that implement one of the reader protocols, by family
        """
        # the readers, by family
        found = {}
        # go through the modules that hold readers
        for name, module in list(sys.modules.items()):
            # skipping everything else
            if not name.startswith(("qed.readers", "qed.stacks")):
                # on to the next
                continue
            # go through the classes each one defines
            for _, cls in inspect.getmembers(module, inspect.isclass):
                # skipping the ones it only imports, and anything that is not a component
                if cls.__module__ != module.__name__ or not issubclass(cls, pyre.component):
                    # on to the next
                    continue
                # a class that implements a reader protocol
                if any(cls.pyre_isCompatible(protocol) for protocol in self.protocols()):
                    # is a reader
                    found[cls.pyre_family()] = cls
        # hand them off
        return found

    def protocols(self) -> tuple:
        """
        The reader protocols: qed's own, and the one of the pipelines
        """
        # both of them
        return (qed.protocols.reader, qed.viz.reader)

    def bookkeeping(self) -> set:
        """
        The names the framework puts on every component class and every flow factory, which are
        not attributes anybody declared
        """

        # a component that declares nothing
        class Component(pyre.component):
            """
            A component that declares nothing
            """

        # and a flow factory that declares nothing
        class Factory(pyre.flow.factory, family="qed.etc.introspection.factory"):
            """
            A flow factory that declares nothing
            """

        # the names on either
        return set(vars(Component)) | set(vars(Factory))

    def survey(self, cls, framework: set) -> dict:
        """
        Record the traits, methods and class-level attributes of the reader {cls}, leaving out
        the names in {framework}
        """
        # the row of the reader
        row = {
            "family": cls.pyre_family(),
            "class": self.origin(klass=cls),
            "implements": [
                protocol.pyre_family()
                for protocol in self.protocols()
                if cls.pyre_isCompatible(protocol)
            ],
            "traits": {},
            "methods": {},
            "attributes": {},
        }
        # its settings, components, inputs and outputs
        for trait in cls.pyre_configurables():
            # are declared by the nearest class whose own declaration names them; the class
            # namespaces cannot tell, since every class carries its inherited traits too
            klass = next(
                (
                    k
                    for k in cls.__mro__
                    if any(t.name == trait.name for t in getattr(k, "pyre_localTraits", ()))
                ),
                None,
            )
            # record it
            row["traits"][trait.name] = {
                "own": klass is cls,
                "from": self.origin(klass=klass),
                "kind": self.kind(trait=trait),
            }
        # its exported behaviors, wherever they come from
        for behavior in cls.pyre_behaviors():
            # are declared by the nearest class that has one by that name
            klass = next((k for k in cls.__mro__ if behavior.name in vars(k)), None)
            # record it
            row["methods"][behavior.name] = {
                "own": klass is cls,
                "from": self.origin(klass=klass),
                "export": True,
            }
        # its other methods, and its class-level attributes, from the qed classes it derives from
        for klass in cls.__mro__:
            # skipping the framework's
            if not klass.__module__.startswith("qed."):
                # on to the next
                continue
            # go through what the class body declares
            for name, value in vars(klass).items():
                # leaving out the special names, the traits, and what a nearer class declared
                if (
                    name.startswith("__")
                    or isinstance(value, pyre.traits.Trait.Trait)
                    or name in row["methods"]
                    or name in row["attributes"]
                ):
                    # on to the next
                    continue
                # a method
                if inspect.isfunction(value) or isinstance(
                    value, (classmethod, staticmethod, property)
                ):
                    # record it
                    row["methods"][name] = {
                        "own": klass is cls,
                        "from": self.origin(klass=klass),
                        "export": False,
                        "kind": self.flavor(value=value),
                    }
                    # on to the next
                    continue
                # anything else that is not the framework's bookkeeping
                if name not in framework:
                    # is a class-level attribute
                    row["attributes"][name] = {
                        "own": klass is cls,
                        "from": self.origin(klass=klass),
                        "value": repr(value)[:60],
                    }
        # hand off the row
        return row

    def kind(self, trait) -> str:
        """
        Classify {trait} as a flow output or input, a component, or a property
        """
        # an output of the flow
        if getattr(trait, "output", False):
            # says so
            return "output"
        # an input of the flow
        if getattr(trait, "input", False):
            # says so
            return "input"
        # a component, or a plain property
        return "component" if trait.isFacility else "property"

    def flavor(self, value) -> str:
        """
        Classify a method found in a class body
        """
        # a class method
        if isinstance(value, classmethod):
            # says so
            return "classmethod"
        # a static method
        if isinstance(value, staticmethod):
            # says so
            return "staticmethod"
        # a property, or an ordinary method
        return "property" if isinstance(value, property) else "method"

    def origin(self, klass) -> str:
        """
        The full name of {klass}, or nothing when there is none
        """
        # the module and the name, if there is a class
        return f"{klass.__module__}.{klass.__qualname__}" if klass is not None else ""


# main
if __name__ == "__main__":
    # instantiate the survey
    app = Readers(name="readers")
    # run it
    status = app.run()
    # and share its status with the shell
    raise SystemExit(status)


# end of file
