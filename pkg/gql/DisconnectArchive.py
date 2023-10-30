# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene
import journal


# the result types
from .Archive import Archive


# remove a data archive from the pile
class DisconnectArchive(graphene.Mutation):
    """
    Disconnect a data archive
    """

    # inputs
    class Arguments:
        # the update context
        uri = graphene.String(required=True)

    # the result is always an archive
    archive = graphene.Field(Archive)

    # the range controller mutator
    def mutate(root, info, uri):
        """
        add a new archive to the pile
        """
        # grab the panel
        panel = info.context["panel"]
        # show me
        channel = journal.info("qed.gql.archives")
        channel.log(f"disconnecting {uri}")
        # and resolve the mutation
        return None


# end of file
