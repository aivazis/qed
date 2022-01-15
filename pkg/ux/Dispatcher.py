# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import journal
import re
# support
import qed

# the query handler
from .GraphQL import GraphQL


# the main request dispatcher
class Dispatcher:
    """
    The handler of web requests
    """


    # interface
    def dispatch(self, plexus, server, request):
        """
        Analyze the {request} received by the {server} and invoke the appropriate {plexus} behavior
        """
        # get the request type
        command = request.command
        # get the request uri
        url = request.url

        # make a channel
        channel = journal.debug("qed.ux.dispatch")
        # and show me
        channel.log(f"{command}: {url}")

        # take a look
        match = self.regex.match(url)
        # if there is no match
        if not match:
            # something terrible has happened
            return server.responses.NotFound(server=server)

        # find who matched
        token = match.lastgroup
        # look up the handler
        handler = getattr(self, token)
        # invoke
        return handler(plexus=plexus, server=server, request=request, match=match)


    # metamethods
    def __init__(self, plexus, docroot, pfs, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the location of my document root so i can serve static assets
        self.docroot = docroot.discover()
        # attach it to the app's private filesystem
        pfs['ux'] = docroot

        # make a spec for the app engine
        spec = 'ux'
        # use the spec to build a name for my panel
        name = f"{plexus.pyre_name}.{spec}"
        # make an instance of the application engine
        self.panel = qed.ux.panel(name=name, spec=spec, plexus=plexus, globalAliases=True)

        # instantiate the {GraphQL} handler
        self.gql = GraphQL(panel=self.panel)

        # all done
        return


    # handlers
    def data(self, plexus, server, match, **kwds):
        """
        Handle a data request
        """
        # make a channel
        channel = journal.info("qed.ux.data")
        # show me
        channel.line(f"reader: {match.group('datasrc')}")
        channel.line(f"dataset: {match.group('dataset')}")
        channel.line(f"channel: {match.group('datachannel')}")
        channel.line(f"zoom: {match.group('zoom')}")
        channel.line(f"tile: {match.group('tile')}")
        # flush
        channel.log()
        # and punt
        return server.documents.OK(server=server)


    def graphql(self, **kwds):
        """
        Handle a {graphql} request
        """
        # delegate to my {graphql} handler
        return self.gql.respond(**kwds)


    def stop(self, plexus, server, **kwds):
        """
        The client is asking me to die
        """
        # log it
        plexus.info.log("shutting down")
        # and exit
        return server.documents.Exit(server=server)


    def document(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.File(uri=uri, server=server, application=plexus)


    def css(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.CSS(uri=uri, server=server, application=plexus)


    def jscript(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.Javascript(uri=uri, server=server, application=plexus)


    def favicon(self, plexus, server, request, **kwds):
        """
        The client requested the app icon
        """
        # we don't have one
        return server.responses.NotFound(server=server)


    def root(self, plexus, server, request, **kwds):
        """
        The client requested the root document
        """
        # form the uri
        uri = "/ux/{0.pyre_namespace}.html".format(plexus)
        # open the document and serve it
        return server.documents.File(uri=uri, server=server, application=plexus)


    # private data
    regex = re.compile("|".join([
        # the data request recognizer; resist the temptation to add commas at the end of
        # these lines...
        r"/(?P<data>data/"
        r"(?P<datasrc>[a-z0-9-]+)/(?P<dataset>[a-z0-9-]+)/(?P<datachannel>[a-z]+)/"
        r"(?P<zoom>[0-9-]+)/(?P<tile>[0-9x+-]+))",
        # graphql requests
        r"/(?P<graphql>graphql)",
        # the kill command
        r"/(?P<stop>stop)",
        # document requests
        r"/(?P<css>.+\.css)",
        r"/(?P<jscript>.+\.js)",
        r"/(?P<document>(graphics/.+)|(fonts/.+))",
        r"/(?P<favicon>favicon.ico)",
        # everything else gets the app page; see the {root} resolver above
        r"/(?P<root>.*)",
        ]))


# end of file
