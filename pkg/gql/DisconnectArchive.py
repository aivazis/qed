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

    # the result is the disconnected archive
    archive = graphene.Field(Archive)

    # the range controller mutator
    def mutate(root, info, uri):
        """
        add a new archive to the pile
        """
        # grab the panel
        panel = info.context["panel"]
        # get the collection of archives
        archives = panel.archives
        # if the {uri} is not already connected
        if uri not in archives:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect '{uri}")
            channel.line(f"the URI does not correspond to a connected data archive")
            # flush
            channel.log()
            # bail, just in case firewall aren't fatal
            return None
        # if it is, get it
        archive = archives[uri]
        # remove it from the pile
        del archives[uri]
        # put it in the mutation resolution context
        context = {"archive": archive}
        # and resolve the mutation
        return context


# end of file
