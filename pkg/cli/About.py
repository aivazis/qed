# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
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
        # make some space
        plexus.info.log(qed.meta.header)
        # all done
        return


    @qed.export(tip="print out the license and terms of use")
    def license(self, plexus, **kwds):
        """
        Print out the license and terms of use of the qed package
        """
        # make some space
        plexus.info.log(qed.meta.license)
        # all done
        return


    @qed.export(tip="print the version number")
    def version(self, plexus, **kwds):
        """
        Print the version of the qed package
        """
        # make some space
        plexus.info.log(qed.meta.header)
        # all done
        return


# end of file
