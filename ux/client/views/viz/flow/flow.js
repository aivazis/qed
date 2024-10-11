// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
import { Camera, Compass } from '~/widgets'

// local
// components
import { Grid } from './grid'
// paint
import styles from './styles'


// the flow panel
export const Flow = ({ viewport, view }) => {
    // get the flow attached to this view
    const { flow } = useFragment(flowVizGetFlowDiagramFragment, view)
    // build a reference to my container so we can measure it and install listeners
    const ref = React.useRef(null)

    // clear the node selection
    const clearSelection = () => {
        // all done
        return
    }

    // assemble the canvas behaviors
    const behaviors = {
        // clear the selection
        onClick: clearSelection,
    }

    // render
    return (
        <section ref={ref} tabIndex="-1" style={styles.panel}>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                {...styles.canvas} {...behaviors}
            >
                <Camera ref={ref} viewport={viewport}>
                    <Compass />
                    <Grid />
                </Camera>
            </svg>
        </section>

    )
}

// my fragment
const flowVizGetFlowDiagramFragment = graphql`
    fragment flowVizGetFlowDiagramFragment on View {
        flow {
            active
        }
    }
`


// end of file
