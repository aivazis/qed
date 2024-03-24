# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import json
import traceback

# support
import qed
import journal


# the {graphql} request handler
class GraphQL:
    """
    The resolver of graphql queries and mutations
    """

    # interface
    def respond(self, store, server, request, **kwds):
        """
        Resolve the {query} and generate a response for the client
        """
        # assemble the raw payload
        raw = b"\n".join(request.payload)
        # if there's nothing there
        if not raw:
            # respond with an empty document; should never happen
            return server.documents.OK(server=server)

        # parse the {request} payload
        payload = json.loads(raw)
        # get the query
        query = payload.get("query")
        # extract the variables
        variables = payload.get("variables")
        # and the operation
        # operation = payload.get("operation")

        # make a fresh copy of my context
        context = dict(self.context)
        # decorate with the info for this request
        context["store"] = store
        context["server"] = server
        context["request"] = request

        # display the {query} details, if the user cares to see
        channel = journal.debug("qed.ux.graphql")
        # if the channel is active
        if channel:
            # mark
            channel.line(f"query:")
            # go through the query representation
            for line in query.strip().splitlines():
                # and print each line
                channel.line(f"    {line}")
            # if there are variable bindings
            if variables:
                # mark
                channel.line(f"  variables:")
                # go through them
                for key, value in variables.items():
                    # and print each binding
                    channel.line(f"    {key}: {value}")
            # flush
            channel.log()

        # execute the query
        result = self.schema.execute(query, context=context, variables=variables)

        # assemble the resulting document
        doc = {"data": result.data}
        # in addition, if something went wrong
        if result.errors:
            # inform the client; pick the first error, since it doesn't seem that the client
            # can get the whole list in a usable way
            doc["errors"] = [{"message": str(result.errors[0].original_error)}]
            # make a channel
            channel = journal.warning("qed.ux.graphql")
            # go through the errors
            for error in result.errors:
                # get the original error
                original = error.original_error
                # format each line of the traceback
                for entry in traceback.format_exception(original):
                    # and report it
                    channel.report(report=entry.splitlines())
            # flush
            channel.log()

        # encode it using JSON and serve it
        return server.documents.JSON(server=server, value=doc)

    # metamethods
    def __init__(self, plexus, dispatcher, store, **kwds):
        # chain up
        super().__init__(**kwds)
        # load my schema and attach it
        self.schema = qed.gql.schema
        # initialize the execution context
        self.context = {
            "plexus": plexus,
            "dispatcher": dispatcher,
            "store": store,
            "nameserver": store.pyre_nameserver,
        }
        # make sure my error channel is not fatal
        journal.error("qed.ux.graphql").fatal = False
        # all done
        return


# end of file
