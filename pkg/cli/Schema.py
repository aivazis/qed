# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# declaration
class Schema(qed.shells.command, family="qed.cli.schema"):
    """
    Export the qed GraphQL schema
    """

    # user configurable state
    stream = qed.properties.ostream()
    stream.doc = "the file to write; stdout by default"

    # interface
    @qed.export(tip="render the GraphQL schema as SDL")
    def sdl(self, **kwds):
        """
        Render the schema as SDL and emit it to my {stream}
        """
        # render the schema body
        body = qed.gql.sdl().strip()
        # assemble the document: preamble, a blank separator, the body, then the marker
        document = "\n".join([*self.preamble, "", "", body, "", "# end of file"])
        # write it out
        print(document, file=self.stream)
        # all done; report success
        return 0

    # the preamble rendered above the SDL body in the generated file
    preamble = (
        "# -*- graphql -*-",
        "#",
        "# michael a.g. aïvázis <michael.aivazis@para-sim.com>",
        "# (c) 1998-2026 all rights reserved",
        "#",
        "# GENERATED FILE -- do not edit by hand",
        "# regenerate with `qed schema sdl`",
        "# source of truth: qed.gql.sdl",
    )


# end of file
