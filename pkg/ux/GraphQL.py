# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import json
import traceback

# third party
import graphql

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
            # make a pile
            messages = []
            # and a channel
            channel = journal.warning("qed.ux.graphql")
            # go through the errors
            for error in result.errors:
                # split it
                lines = str(error).splitlines()
                # report the {graphql} error
                channel.line(f"graphql:")
                channel.indent()
                channel.report(report=lines)
                channel.outdent()
                # add the error to the pile
                messages.extend(lines)
                # get the original error
                original = error.original_error
                # if it is non-trivial
                if original:
                    # report it
                    channel.line()
                    channel.line(f"python:")
                    channel.indent()
                    # format each line of the traceback
                    for entry in traceback.format_exception(original):
                        # split
                        lines = entry.splitlines()
                        # report it
                        channel.report(report=lines)
                        # and add it to the message pile
                        messages.extend(lines)
                    channel.outdent()
                # flush
                channel.log()
            # finally, add the error report to the document
            doc["errors"] = [{"message": "\n".join(messages)}]

        # if this request was a mutation that succeeded, the server state changed; notify every
        # live client so it can refetch. this is the single broadcast choke point: every state
        # change arrives as a mutation POST, and they all funnel through here
        if not result.errors and self._isMutation(query=query):
            # push a minimal change notification to all subscribers
            self._notify(server=server)

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

    # implementation details
    def _isMutation(self, query):
        """
        Determine whether {query} carries a mutation operation
        """
        # parse the query; this is safe because we only ask after a successful execution
        document = graphql.parse(query)
        # report whether any of its operations is a mutation
        return any(
            getattr(definition, "operation", None) is graphql.OperationType.MUTATION
            for definition in document.definitions
        )

    def _notify(self, server):
        """
        Push a change notification to every live client subscribed to {server}'s hub
        """
        # the notification frame is constant, so build it once
        if self._changeFrame is None:
            # use the {EventStream} framing so the wire format lives in one place
            stream = server.eventStream(server=server)
            # a minimal payload: clients treat any message as "refetch your state"
            self._changeFrame = stream.event(json.dumps({"type": "change"}))
        # broadcast it on the global topic; coalesce, since every change frame is identical, so a
        # burst of mutations collapses to a single pending "refetch" per client rather than a storm
        server.hub.publish(self._changeFrame, coalesce=True)
        # all done
        return

    # private data
    _changeFrame = None


# end of file
