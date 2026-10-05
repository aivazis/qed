// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// whether the viewport syncs live
import { useLive } from '../viz/useLive'

// local
// the canvas
import { Canvas } from './canvas'


// the pipeline of the view in {viewport}, drawn on a canvas
export const Flow = ({ viewport, view }) => {
    // get the diagram of the pipeline of the view
    const { diagram } = useFragment(flowVizGetFlowDiagramFragment, view)
    // a live viewport sends every step of a drag to the server
    const { enabled: live } = useLive(viewport)
    // render
    return (
        <Canvas diagram={diagram} live={live} />
    )
}


// my fragment
const flowVizGetFlowDiagramFragment = graphql`
    fragment flowVizGetFlowDiagramFragment on View {
        # the diagram of the pipeline
        diagram {
            ...canvasFlowDiagramFragment
        }
    }
`


// end of file
