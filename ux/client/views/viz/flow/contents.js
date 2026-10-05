// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql } from 'react-relay/hooks'


// everything the client draws of a pipeline diagram; the mutations that change the diagram ask
// for it, so their responses replace the whole picture
export const contentsFlowDiagramFragment = graphql`
    fragment contentsFlowDiagramFragment on FlowDiagram {
        # the parts
        ...labelsFlowDiagramFragment
        ...connectorsFlowDiagramFragment
        ...slotsFlowDiagramFragment
        ...factoriesFlowDiagramFragment
        # where the nodes are, for the camera and the drop feedback
        factories {
            id
            at {
                x
                y
                z
            }
            # what the inspector shows
            family
            doc
            traits {
                name
                kind
                type
                value
                default
                doc
            }
        }
        slots {
            id
            at {
                x
                y
                z
            }
            bound
        }
    }
`

// end of file
