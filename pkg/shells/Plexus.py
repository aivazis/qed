# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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

    views = qed.properties.list(schema=qed.protocols.ux.view())
    views.doc = "the initial list of views"

    # the reader to use for all datasets that don't specify one
    reader = qed.properties.str(default=None)
    reader.aliases = {"r"}
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
    shape.doc = "the shape of the dataset, in (lines x samples)"

    # shorthands for specifying shape parts
    lines = qed.properties.int(default=None)
    lines.aliases = {"rows", "lines", "l"}
    lines.doc = "set the vertical dimension of the dataset"

    samples = qed.properties.int(default=None)
    samples.aliases = {"cols", "columns", "s"}
    samples.doc = "set the horizontal dimension of the dataset"

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

        # sort out my cell configuration, since it has multiple ways of being set
        yield from self._configureCell()
        # configure my shape
        yield from self._configureShape()
        # load any datasets from the command line
        yield from self._loadDatasets()

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

    # implementation detail
    def _configureCell(self):
        """
        Resolve the configuration of my cell type
        """
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
        # if it's not an explicit cell assignment
        if winner != "cell":
            # override
            self.cell = winner
        # return with no configuration errors
        return []

    def _configureShape(self):
        """
        Resolve the configuration of my shape
        """
        # initialize my shape candidate
        shape = list(self.shape) if self.shape else [0, 0]
        # get the priority of the shape setting
        shapePriority = self.pyre_inventory.getTraitPriority(self.pyre_trait("shape"))
        # get the number of lines
        lines = self.lines
        # if it's non-trivial
        if lines:
            # get its priority
            linesPriority = self.pyre_inventory.getTraitPriority(
                self.pyre_trait("lines")
            )
            # if it's greater than shape's
            if linesPriority > shapePriority:
                # override
                shape[0] = lines
        # get the number of samples
        samples = self.samples
        # if it's non-trivial
        if samples:
            # get its priority
            samplesPriority = self.pyre_inventory.getTraitPriority(
                self.pyre_trait("samples")
            )
            # if it's greater than shape's
            if samplesPriority > shapePriority:
                # override
                shape[1] = samples
        # if the resulting shape has a non-trivial entry
        if shape[0] or shape[1]:
            # store it
            self.shape = shape
        # all done
        return []

    def _loadDatasets(self):
        """
        Load datasets from the command line
        """
        # get the command line
        argv = tuple(self.argv)
        # if there are no command line arguments
        if not argv:
            # nothing to do here
            return
        # get the name of all documented actions
        names = tuple(name for _, name, _, _ in self.pyre_documentedActions())
        # if the first command line argument is an action
        if argv and argv[0] in names:
            # go no further; let the action handle the command line
            return
        # otherwise, interpret all command line arguments arguments as files to read
        # consume the command line so we bypass the panel dispatch in {main}
        argv = tuple(
            command.command for command in self.pyre_configurator.consumeCommands()
        )
        # i need a reader
        reader = self.reader
        # if i don't have one
        if not reader:
            # make a channel
            channel = journal.error("qed.cli")
            # complain
            channel.line(f"while attempting to load '{argv[0]}'")
            channel.line(f"no registered reader")
            channel.line(f"please specify the reader using the '--reader' option")
            # flush
            channel.log()
            # complain
            yield f"unknown reader; please specify one using '--reader'"
            # and bail
            return
        # we have a setting; attempt to
        try:
            # resolve the reader
            factory = qed.protocols.reader.pyre_resolveSpecification(spec=reader)
        # if not
        except self.ResolutionError as error:
            # make a channel
            channel = journal.error("qed.cli")
            # complain
            channel.line(f"unknown reader '{self.reader}'")
            channel.line(f"while attempting to resolve the dataset reader")
            # flush
            channel.log()
            # complain
            yield f"could not resolve '{reader}'"
            # and bail
            return
        # go through the arguments
        for uri in argv:
            # prep the reader configuration
            args = {
                "name": self._datasetName(),
                "uri": uri,
            }
            # if i have a non-trivial cell
            if self.cell:
                # add it to the pile
                args["cell"] = self.cell
            # if i have a non-trivial shape
            if self.shape:
                # add it to the pile
                args["shape"] = self.shape
            # attempt to
            try:
                # instantiate the reader
                reader = factory(**args)
            # if anything goes wrong
            except Exception as error:
                # make a channel
                channel = journal.warning("qed.cli")
                # complain
                channel.line(f"could not load datasets from '{uri}'")
                channel.line(f"while processing the command line")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # complain
                yield f"could not instantiate '{reader}'"
                # and move on
                continue
            # if all goes well, register the reader
            self.datasets.append(reader)
        # clear out
        # all done
        return

    def _datasetName(self):
        """
        Build a nickname for a new dataset
        """
        # increment the counter
        self._ds += 1
        # make a name and return it
        return f"qed_{self._ds:02}"

    # private data
    _ds = 0
    _ux = None  # the UX manager


# end of file
