# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import textwrap

# framework access
import pyre
import journal

# and my package
import qed


# declaration
class Plexus(pyre.plexus, family="qed.shells.plexus"):
    """
    The main action dispatcher
    """

    # types
    from .Action import Action as pyre_action

    # the known archives
    archives = qed.properties.list(schema=qed.protocols.archive())
    archives.default = [qed.archives.local(name="local:workspace")]
    archives.doc = "the list of registered data archives"

    # the pile of known datasets
    datasets = qed.properties.list(schema=qed.protocols.reader())
    datasets.doc = "the list of datasets to display"
    datasets.aliases = {"ds"}

    # the reader to use for all datasets that don't specify one
    reader = qed.properties.str()
    reader.default = None
    reader.doc = "the reader to use when opening datasets"

    # individual metadata, used to assemble a default layout
    cell = qed.protocols.datatype()
    cell.default = None
    cell.doc = "the format string that specifies the type of the dataset payload"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = (0, 0)
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    # shorthands for selecting the cell type
    # the aliases provide {mdx} compatibility
    uint8 = qed.properties.bool(default=False)
    uint8.aliases = {"byte", "b1", "u1"}
    uint8.doc = "set the cell type to an unsigned 8-bit integer"

    uint16 = qed.properties.bool(default=False)
    uint16.aliases = {"byte2", "b2", "u2"}
    uint16.doc = "set the cell type to an unsigned 16-bit integer"

    uint32 = qed.properties.bool(default=False)
    uint32.aliases = {"u4"}
    uint32.doc = "set the cell type to an unsigned 32-bit integer"

    uint64 = qed.properties.bool(default=False)
    uint64.aliases = {"u8"}
    uint64.doc = "set the cell type to an unsigned 64-bit integer"

    int8 = qed.properties.bool(default=False)
    int8.aliases = {"i1", "integer*1"}
    int8.doc = "set the cell type to an 8-bit integer"

    int16 = qed.properties.bool(default=False)
    int16.aliases = {"i2", "integer*2"}
    int16.doc = "set the cell type to a 16-bit integer"

    int32 = qed.properties.bool(default=False)
    int32.aliases = {"i4", "integer*4"}
    int32.doc = "set the cell type to a 32-bit integer"

    int64 = qed.properties.bool(default=False)
    int64.aliases = {"i8", "integer*8"}
    int64.doc = "set the cell type to a 64-bit integer"

    float32 = qed.properties.bool(default=False)
    float32.aliases = {"r4", "real*4"}
    float32.doc = "set the cell type to a 32-bit float"

    float64 = qed.properties.bool(default=False)
    float64.aliases = {"r8", "real*8"}
    float64.doc = "set the cell type to a 64-bit float"

    complex64 = qed.properties.bool(default=False)
    complex64.aliases = {"c8", "complex*8"}
    complex64.doc = "set the cell type to a 64-bit complex"

    complex128 = qed.properties.bool(default=False)
    complex128.aliases = {"c16", "complex*16"}
    complex128.doc = "set the cell type to a 32-bit complex"

    # journal control; useful until journal is once again configurable
    logfile = qed.properties.path()
    logfile.default = None
    logfile.doc = "file that captures all journal output"

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # if i have a logfile
        if self.logfile:
            # redirect all journal output to the file
            journal.logfile(name=str(self.logfile), mode="a")
        # all done
        return

    # pyre framework hooks
    def pyre_configured(self, **kwds):
        """
        Hook invoked when the app configuration is complete
        """
        # chain up and pass on any configuration errors
        yield from super().pyre_configured()

        # process the cell by running a competition among all the ways it could be specified
        # first, collect my type traits in a pile
        types = [
            "uint8",
            "uint16",
            "uint32",
            "uint64",
            "int8",
            "int16",
            "int32",
            "int64",
            "float32",
            "float64",
            "complex64",
            "complex128",
        ]
        # find the ones that are active
        active = [name for name in types if getattr(self, name)]
        # sort the list
        ranked = sorted(
            # include {cell} in the pile so we know where it stands
            active + ["cell"],
            # the key is the trait priority
            key=lambda name: self.pyre_inventory.getTraitPriority(
                self.pyre_trait(name)
            ),
        )
        # the winner is
        winner = ranked[-1]
        # if it's not and explicit cell assignment
        if winner != "cell":
            # override
            self.cell = winner

        # all done
        return

    # support for the help system
    def pyre_banner(self):
        """
        Generate the help banner
        """
        # the project header
        yield from textwrap.dedent(qed.meta.banner).splitlines()
        # the doc string
        yield from self.pyre_showSummary(indent="")
        # the authors
        yield from textwrap.dedent(qed.meta.authors).splitlines()
        # all done
        return

    # interactive session management
    def pyre_interactiveSessionContext(self, context=None):
        """
        Go interactive
        """
        # prime the execution context
        context = context or {}
        # grant access to my package
        context["qed"] = qed  # my package
        # and chain up
        return super().pyre_interactiveSessionContext(context=context)

    # virtual filesystem configuration
    def pyre_mountApplicationFolders(self, pfs, prefix, **kwds):
        """
        Explore the application installation folders and construct my private filespace
        """
        # chain up
        pfs = super().pyre_mountApplicationFolders(pfs=pfs, prefix=prefix, **kwds)
        # get my namespace
        namespace = self.pyre_namespace

        #
        # this is early times, so {prefix} may not be explored; tread carefully
        #

        # gingerly, look for the web document root, but avoid expanding parts of the local
        # filesystem that we don't care about and getting trapped in deep directory structures
        # start at the top
        docroot = prefix
        # and descend where we think the main static asset is
        for name in ["etc", namespace, "ux"]:
            # fill the contents of the current node
            docroot.discover(levels=1)
            # attempt to
            try:
                # descend to the next level
                docroot = docroot[name]
            # if not there
            except prefix.NotFoundError:
                # grab a channel
                channel = self.warning
                # complain
                channel.line(f"while looking for UX support:")
                channel.line(f"directory '{docroot.uri}/{name}' not found")
                channel.line(f"disabling the web shell")
                channel.log()
                # mark the UX as unavailable
                self._ux = None
                # and bail
                break
        # if all goes well and we reach the intended folder without errors
        else:
            # instantiate and attach my dispatcher
            self._ux = qed.ux.dispatcher(plexus=self, docroot=docroot, pfs=pfs)

        # all done
        return pfs

    # main entry point for the web shell
    def pyre_respond(self, server, request):
        """
        Fulfill an HTTP request
        """
        # get my dispatcher
        ux = self._ux
        # if i don't have one, there is something wrong with my installation
        if ux is None:
            # so everything is an error
            return server.responses.NotFound(server=server)

        # otherwise, ask the dispatcher to do its thing
        return ux.dispatch(plexus=self, server=server, request=request)

    # private data
    _ux = None  # the UX manager

    _typemap = {}


# end of file
