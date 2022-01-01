# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# declaration
class Config(qed.shells.command, family="qed.cli.config"):
    """
    Display configuration information about this package
    """


    # version info
    @qed.export(tip="the version information")
    def version(self, **kwds):
        """
        Print the version of the qed package
        """
        # print the version number
        print(f"{qed.meta.version}")
        # all done
        return 0


    # configuration
    @qed.export(tip="the top level installation directory")
    def prefix(self, **kwds):
        """
        Print the top level installation directory
        """
        # print the installation location
        print(f"{qed.prefix}")
        # all done
        return 0


    @qed.export(tip="the directory with the executable scripts")
    def path(self, **kwds):
        """
        Print the location of the executable scripts
        """
        # print the path to the bin directory
        print(f"{qed.prefix}/bin")
        # all done
        return 0


    @qed.export(tip="the directory with the python packages")
    def pythonpath(self, **kwds):
        """
        Print the directory with the python packages
        """
        # print the path to the python package
        print(f"{qed.home.parent}")
        # all done
        return 0


    @qed.export(tip="the location of the {qed} headers")
    def incpath(self, **kwds):
        """
        Print the locations of the {qed} headers
        """
        # print the path to the headers
        print(f"{qed.prefix}/include")
        # all done
        return 0


    @qed.export(tip="the location of the {qed} libraries")
    def libpath(self, **kwds):
        """
        Print the locations of the {qed} libraries
        """
        # print the path to the libraries
        print(f"{qed.prefix}/lib")
        # all done
        return 0


# end of file
