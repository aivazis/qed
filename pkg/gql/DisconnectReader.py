# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .Reader import Reader


# remove a data reader from the pile
class DisconnectReader(graphene.Mutation):
    """
    Disconnect a data reader
    """

    # inputs
    class Arguments:
        # the update context
        name = graphene.String(required=True)

    # the result is the disconnected reader
    reader = graphene.Field(Reader)

    # the range controller mutator
    def mutate(root, info, name):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        reader = store.reader(name=name)
        # if it's not there
        if not reader:
            # we have a bug
            channel = journal.firewall("qed.gql.disconnect")
            # complain
            channel.line(f"while attempting to disconnect '{name}")
            channel.line(f"the URI does not correspond to a connected product reader")
            # flush
            channel.log()
            # bail, just in case firewall aren't fatal
            return None
        # remove it from the pile
        store.disconnectReader(name=name)
        # go through its datasets
        for dataset in reader.datasets:
            # and remove each one from the dataset registry
            store.disconnectDataset(name=dataset.pyre_name)
        # form the mutation resolution context
        context = {"reader": reader}
        # and resolve the mutation
        return context


# end of file
