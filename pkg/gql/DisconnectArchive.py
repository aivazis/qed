# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


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

    # the result is the disconnected archive
    archive = graphene.Field(Archive)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, uri):
        """
        Remove an archive from the pile
        """
        # grab the store
        store = info.context["store"]
        # get the archive
        archive = store.archive(uri=uri)
        # if the {uri} is not already connected
        if not archive:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect '{uri}")
            channel.line(f"the URI does not correspond to a connected data archive")
            # flush
            channel.log()
            # bail, just in case firewall aren't fatal
            return None
        # remove it from the pile
        store.disconnectArchive(uri=uri)
        # put it in the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
