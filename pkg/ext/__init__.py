# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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
except ImportError:
    # indicate the bindings are not accessible
    libqed = None

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
