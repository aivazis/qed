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
        # what the canvas draws
        ...canvasFlowDiagramFragment
        # and what the inspector shows of the factories
        factories {
            id
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
    }
`


// end of file
