# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal

# the request payload
from .ReconfigureEarthAccessArchiveInput import ReconfigureEarthAccessArchiveInput

# the conversion of the payload into the query of an archive
from .ConnectEarthAccessArchive import ConnectEarthAccessArchive

# the result types
from .Archive import Archive


# replace the query of a connected earth access archive
class ReconfigureEarthAccessArchive(graphene.Mutation):
    """
    Reconfigure an earth access archive, keeping its name and its location unless the user
    renamed it
    """

    # inputs
    class Arguments:
        # the request payload
        input = ReconfigureEarthAccessArchiveInput(required=True)

    # the result is the reconfigured archive
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Replace the query of the archive at {input.uri}
        """
        # grab the store
        store = info.context["store"]
        # look up the archive
        archive = store.archive(uri=input.uri)
        # the client edits archives it was told about, so one that is missing, or of another
        # kind, means the two have drifted apart
        if archive is None or archive.tag != "earth":
            # make a channel
            channel = journal.firewall("qed.gql.reconfigure")
            # complain
            channel.line(f"no earth access archive at '{input.uri}'")
            # say what was going on
            channel.line("while reconfiguring its query")
            # flush
            channel.log()
            # and bail, in case firewalls aren't fatal
            return None
        # assemble the query out of the payload
        query = ConnectEarthAccessArchive.harvest(input=input)
        # a payload that does not form a query has already been reported
        if query is None:
            # so bail
            return None
        # the new query replaces the old one, so every constraint it leaves out is cleared
        settings = {name: query.get(name) for name in archive.constraints}
        # reconfigure the archive, in place unless the user renamed it
        archive = store.reconfigureArchive(
            uri=input.uri,
            location=input.location or input.uri,
            settings=settings,
            name=input.name,
        )
        # put it in the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
