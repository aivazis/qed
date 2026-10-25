# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal

# the request payload
from .ReconfigureArchiveInput import ReconfigureArchiveInput

# the result types
from .Archive import Archive


# point a connected data archive at a new location
class ReconfigureArchive(graphene.Mutation):
    """
    Reconfigure a data archive, keeping its name
    """

    # inputs
    class Arguments:
        # the request payload
        input = ReconfigureArchiveInput(required=True)

    # the result is the reconfigured archive
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Point the archive at {input.uri} to {input.location}
        """
        # grab the store
        store = info.context["store"]
        # the settings, with an empty value standing for a setting the user cleared
        tokens = input.credentials.tokens if input.credentials else []
        # turn them into a table
        settings = {token["name"]: token["value"] or None for token in tokens}
        # reconfigure the archive
        archive = store.reconfigureArchive(
            uri=input.uri, location=input.location, settings=settings
        )
        # if that failed
        if archive is None:
            # make a channel
            channel = journal.warning("qed.gql.reconfigure")
            # complain
            channel.log(f"could not reconfigure the archive at '{input.uri}'")
            # and resolve the mutation with nothing
            return None
        # put it in the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
