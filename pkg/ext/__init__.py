# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Standardized access to CPU and GPU acceleration

The following conditions must all be true before we can provide CUDA support:

 - the local host must have CUDA libraries and drivers
 - pyre must have been built with CUDA support
 - qed must have been built with CUDA support
 - the current host must have at least one compatible device
"""

# attempt to
try:
    # pull the extension module
    from . import qed as libqed
# if this fails
except ImportError as error:
    # indicate the bindings are not accessible
    libqed = None
    # remember why, for whoever has to explain a failure downstream: a server without its
    # extension declines to come up, and a product without it cannot read its cells, and both
    # quote this
    libqed_error = str(error)
    # leave a note for the curious; not a warning, since a command line panel that never
    # renders, e.g. the one that generates the schema while the extension is still being built,
    # must be able to carry on quietly
    import journal

    # make a channel
    channel = journal.debug("qed.ext")
    # complain
    channel.line("the qed extension could not be imported")
    channel.line(f"{error}")
    # flush
    channel.log()
# if it succeeds
else:
    # there is no failure to explain
    libqed_error = None

# check whether
try:
    # pyre has CUDA support
    import cuda
# if not
except ImportError:
    # indicate that there is no CUDA support
    libqed_cuda = None
# if it does
else:
    # if the current host doesn't have any available devices
    if cuda.manager.count == 0:
        # indicate there is no CUDA support
        libqed_cuda = None
    # otherwise
    else:
        # attempt to
        try:
            # get the CUDA extension module
            from . import qed_cuda as libqed_cuda
        # if it can't be imported
        except ImportError:
            # again, no CUDA support
            libqed_cuda = None


# end of file
