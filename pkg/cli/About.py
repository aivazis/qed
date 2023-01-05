# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import journal
import qed


# declaration
class About(qed.shells.command, family='qed.cli.about'):
    """
    Display information about this application
    """


    @qed.export(tip="print the copyright note")
    def copyright(self, plexus, **kwds):
        """
        Print the copyright note of the qed package
        """
        # show the copyright note
        plexus.info.log(qed.meta.copyright)
        # all done
        return


    @qed.export(tip="print out the acknowledgments")
    def credits(self, plexus, **kwds):
        """
        Print out the license and terms of use of the qed package
        """
        # show the package header
        plexus.info.log(qed.meta.header)
        # all done
        return


    @qed.export(tip="print out the license and terms of use")
    def license(self, plexus, **kwds):
        """
        Print out the license and terms of use of the qed package
        """
        # show the package license
        plexus.info.log(qed.meta.license)
        # all done
        return


    @qed.export(tip="print the version number")
    def version(self, plexus, **kwds):
        """
        Print the version of the qed package
        """
        # make a channel
        channel = journal.help("qed.about.version")

        # get the package version
        major, minor, micro, revision = qed.version()
        # show it
        channel.line(f"package: {major}.{minor}.{micro} rev {revision}")

        # get the bindings
        libqed = qed.libqed
        # if there are bindings
        if libqed:
            channel.line()
            channel.line(f"libqed:")
            # get the library version
            major, minor, micro, revision = libqed.libVersion
            # show it
            channel.line(f"  library: {major}.{minor}.{micro} rev {revision}")
            # get the version of the bindings
            major, minor, micro, revision = libqed.extVersion
            # show it
            channel.line(f"  bindings: {major}.{minor}.{micro} rev {revision}")

        # get the CUDA bindings
        libqed_cuda = qed.libqed_cuda
        # if there are bindings
        if libqed_cuda:
            channel.line()
            channel.line(f"libqed_cuda:")
            # get the library version
            major, minor, micro, revision = libqed_cuda.libVersion
            # show it
            channel.line(f"  library: {major}.{minor}.{micro} rev {revision}")
            # get the version of the bindings
            major, minor, micro, revision = libqed_cuda.extVersion
            # show it
            channel.line(f"  bindings: {major}.{minor}.{micro} rev {revision}")

        # flush
        channel.log()

        # all done
        return


# end of file
