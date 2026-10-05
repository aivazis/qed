// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// colors
import { theme } from '~/palette'
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
    // a channel without a description has no diagram
    if (diagram === null) {
        // so say so
        return (
            <Missing data-qed-diagram="">
                there is no description of the pipeline of this channel yet
            </Missing>
        )
    }
    // otherwise, draw it
    return (
        <Canvas diagram={diagram} live={live} />
    )
}


// the note in place of a diagram that is not there
const Missing = styled.section`
    flex: 1 1 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: inconsolata;
    font-size: 90%;
    color: ${theme.page.dim};
    cursor: default;
`


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
