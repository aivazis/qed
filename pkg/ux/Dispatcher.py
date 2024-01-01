# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import journal
import re
import urllib
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
        channel = journal.debug("qed.ux.dispatch.url")
        # and show me the {url}
        channel.log(f"{command}: {url}")

        # take a look
        match = self.regex.match(url)
        # if there is no match
        if not match:
            # we have a bug
            channel = journal.firewall("qed.ux.dispatch")
            # complain
            channel.line(f"could not find handler")
            channel.line(f"while resolving ${url}")
            # flush
            channel.log()
            # and return an error to the client
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
        self.panel = qed.ux.panel(name=name, spec=spec, plexus=plexus, docroot=docroot,
            globalAliases=True)

        # instantiate the {GraphQL} handler
        self.gql = GraphQL(panel=self.panel)

        # all done
        return


    # handlers
    def data(self, server, match, **kwds):
        """
        Handle a data request
        """
        # unpack
        data = match.group('data_dataset')
        channel = match.group('data_channel')
        zoom = int(match.group('data_zoom'))
        spec = match.group('data_tile')
        origin = tuple(map(int, match.group('data_origin').split("x")))
        shape = tuple(map(int, match.group('data_shape').split("x")))

        # attempt to
        try:
            # process the request
            tile = self.panel.tile(
                data=data, channel=channel, zoom=zoom, origin=origin, shape=shape)
        # if anything goes wrong while looking up the data sources
        except KeyError:
            # we have a bug
            chnl = journal.firewall("qed.ux.dispatch")
            # complain
            chnl.line(f"could not find data source {data}")
            # flush
            chnl.log()
            # let the client know
            return server.responses.NotFound(server=server)
        # if anything else goes wrong
        except Exception as error:
            # we have a problem
            chnl = journal.error("qed.ux.dispatch")
            # show me
            chnl.line(str(error))
            chnl.line(f"while fetching a tile of '{channel}' from '{data}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"at zoom level {zoom}")
            # and flush
            chnl.log()
            # let the client know
            return server.responses.NotFound(server=server)

        # if all went well, we have a {tile} in memory; attempt to
        try:
            # build the response
            response = server.documents.BMP(server=server, bmp=memoryview(tile))
            # get the dataset name
            dataname = self.panel.dataset(data).pyre_name
            # suggest a file name, in case the user wants to save the tile
            filename = f"{dataname}.{channel}.{zoom}.{spec}.bmp"
            # encode it
            encoded = urllib.parse.quote(filename)
            # decorate it
            response.headers["Content-disposition"] = (
                f'attachment; '
                f'filename="{filename}"; '
                f'filename*={encoded}'
            )
            # and return it
            return response

        # if anything goes wrong
        except Exception as error:
            # we have a problem
            chnl = journal.error("qed.ux.dispatch")
            # show me
            chnl.line(str(error))
            chnl.line(f"while generating a '{channel}' tile of '{data}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"at zoom level {zoom}")
            # and flush
            chnl.log()
        # let the client know
        return server.responses.NotFound(server=server)


    def graphql(self, **kwds):
        """
        Handle a {graphql} request
        """
        # delegate to my {graphql} handler
        return self.gql.respond(dispatcher=self, panel=self.panel, **kwds)


    def profile(self, server, match, request, **kwds):
        """
        Handle a request for a dataset profile
        """
        # unpack
        data = match.group('profile_dataset')
        encoding = match.group('profile_format')
        # the url contains the points of interest
        url = request.url
        # extract the query part
        _, query = url.split("?")
        # points are separated by "&", coordinates by ","
        points = tuple(tuple(map(int, point.split(','))) for point in query.split('&'))

        # generate the profile along with a suggestion for the download name
        filename, profile = self.panel.profile(data=data, points=points, encoding=encoding)

        # get the document factory
        document = getattr(server.documents, encoding)
        # build the response
        response = document(server=server, value=profile)
        # decorate it
        response.headers["Content-disposition"] = f'attachment; filename="{filename}"'
        # and send it off
        return response


    # basic handlers
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
    # recognizer fragments
    uuid = r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
    pyreid = r"[^&?#:\s]+"
    zoom = r"-?\d+"
    origin = r"-?\d+x-?\d+"
    shape = r"\d+x\d+"
    # currently, only {csv} is supported
    profileFormat = r"(CSV)"

    # the app api
    regex = re.compile("|".join([
        # the data request recognizer
        r"/(?P<data>data/" + "/".join([
            rf"(?P<data_dataset>{pyreid})",
            r"(?P<data_channel>\w+)",
            rf"(?P<data_zoom>{zoom})",
            rf"(?P<data_tile>(?P<data_origin>{origin})\+(?P<data_shape>{shape}))"
        ]) + ")",

        # data profile requests
        r"/(?P<profile>profile/" + "/".join([
           rf"(?P<profile_format>{profileFormat})",
           rf"(?P<profile_dataset>{pyreid})",
        ]) + ")",

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
