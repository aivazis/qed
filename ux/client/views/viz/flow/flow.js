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
// diagram nodes
import { Connectors } from './connectors'
import { Factories } from './factories'
import { Labels } from './labels'
import { Slots } from './slots'
// paint
import styles from './styles'


// the flow panel
export const Flow = ({ viewport, view }) => {
    // get the flow attached to this view
    const { diagram } = useFragment(flowVizGetFlowDiagramFragment, view)
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
                {/* everything that is in ICS */}
                <Camera ref={ref} viewport={viewport} scale={20}>
                    {/* the orientation marker at the origin */}
                    {/* <Compass /> */}
                    {/* the current cell highlighter */}
                    <Grid />
                    {/* labels */}
                    <Labels diagram={diagram} />
                    {/* connector */}
                    <Connectors diagram={diagram} />
                    {/* slots */}
                    <Slots diagram={diagram} />
                    {/* factories */}
                    <Factories diagram={diagram} />
                </Camera>
            </svg>
        </section>

    )
}

// my fragment
const flowVizGetFlowDiagramFragment = graphql`
    fragment flowVizGetFlowDiagramFragment on View {
        # extract the diagram
        diagram {
            # metadata
            id
            name
            family
            # labels
            ...labelsFlowDiagramFragment
            # connectors
            ...connectorsFlowDiagramFragment
            # slots
            ...slotsFlowDiagramFragment
            # factories
            ...factoriesFlowDiagramFragment
        }
    }
`


// end of file
