# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the controllers of the channels of a dataset that govern the same quantity
def couple(*, pipeline, context: str, shared: dict):
    """
    Hand {pipeline} the controllers it shares with the other channels of its dataset: every
    controller whose trait declares the quantity it governs is replaced by the one controller
    of that quantity in {shared}, which is made the first time a channel asks for it and is
    named after the quantity under the {context} of the dataset, so its configuration lives at
    {context}.controllers.{quantity}
    """
    # go through the controllers of the channel
    for trait in pipeline.pyre_facilities():
        # the quantity the controller governs, if the channel shares it
        quantity = getattr(trait, "quantity", None)
        # a controller that belongs to its channel alone
        if quantity is None:
            # stays where it is
            continue
        # look for the controller of this quantity
        controller = shared.get(quantity)
        # the first channel to ask for it
        if controller is None:
            # makes it, of the kind the channel uses, configured from its own name
            controller = type(getattr(pipeline, trait.name))(
                name=f"{context}.controllers.{quantity}"
            )
            # and leaves it for the others
            shared[quantity] = controller
        # hand it to the channel
        setattr(pipeline, trait.name, controller)
    # hand the channel back
    return pipeline


# end of file
