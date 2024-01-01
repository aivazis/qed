# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import textwrap

# access the pyre framework
import pyre

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

    # individual metadata, used to assemble a default layout
    cell = qed.protocols.datatype()
    cell.default = None
    cell.doc = "the format string that specifies the type of the dataset payload"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = None
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    # the reader to use for all datasets that don't specify one
    reader = qed.protocols.reader()
    reader.default = None
    reader.doc = "the component that understands the data encoding of a dataset"

    # pyre framework hooks
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


# end of file
