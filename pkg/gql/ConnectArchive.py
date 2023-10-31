# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene
import journal
import qed

# the result types
from .Archive import Archive


# add a new data archive to the pile
class ConnectArchive(graphene.Mutation):
    """
    Connect a new data archive
    """

    # inputs
    class Arguments:
        # the update context
        name = graphene.String(required=True)
        uri = graphene.String(required=True)

    # the result is always an archive
    archive = graphene.Field(Archive)

    # the range controller mutator
    def mutate(root, info, name, uri):
        """
        Add a new archive to the pile
        """
        # grab the panel
        panel = info.context["panel"]
        # get the collection of archives
        archives = panel.archives
        # if the {uri} is already connected
        if uri in archives:
            # bail
            return None
        # parse it
        uri = qed.primitives.uri.parse(uri, scheme="file")
        # if this is a local archive
        if uri.scheme == "file":
            # mount it
            archive = qed.archives.local(name=name, uri=uri)
        # if it's an archive in an S3 bucket
        elif uri.scheme == "s3":
            # mount it
            archive = qed.archives.s3(name=name, uri=uri)
        # anything else
        else:
            # is an error
            return None
        # add the new one to the pile
        archives[str(uri)] = archive
        # make a resolution context
        context = {
            "archive": archive,
        }
        # and resolve the mutation
        return context


# end of file
