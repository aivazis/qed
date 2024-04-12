// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useViewports } from '../viz/useViewports'
// components
import { Measure } from './measure'
import { Sync } from './sync'
import { Viz } from './viz'
import { Zoom } from './zoom'
// styles
import styles from './styles'


// export the activity panel
export const Controls = ({ qed }) => {
    // the active viewport
    const { activeViewport } = useViewports()
    // unpack the views
    const { views } = useFragment(controlsGetDatasetAndChannelInViewFragment, qed)
    // get the active view
    const view = views[activeViewport]
    // unpack what i need
    const { dataset, channel } = view
    // disable some trays if either dataset or channel are trivial
    const enabled = (dataset != null) && (channel != null)

    // render
    return (
        <React.Suspense fallback={<Loading />}>
            {/* the title of the panel */}
            <Header title="controls" style={styles.header} />
            {/* controls for the measuring layer */}
            {enabled && <Measure viewport={activeViewport} view={view} />}
            {/* the controls common to all datasets */}
            {enabled && <Zoom viewport={activeViewport} view={view} />}
            {/* visualization pipeline controls */}
            {enabled && <Viz viewport={activeViewport} view={view} />}
            {/* viewport synchronization controls */}
            {enabled && <Sync qed={qed} />}
        </React.Suspense>
    )
}


const Loading = styled.div`
    font-family: inconsolata;
    font-size: 75%;
    cursor: default;
    padding: 0.25rem;
    content: "loading";
`

// the fragment
const controlsGetDatasetAndChannelInViewFragment = graphql`
    fragment controlsGetDatasetAndChannelInViewFragment on QED {
        views {
            dataset {
                id
            }
            channel {
                id
            }
            # for the measure control
            ...measureControlsGetMeasureLayerStateFragment
            # for the peek context
            ...contextPeekMeasureGetDatasetFragment
            # for figuring out which pixel to peek through
            ...useUpdatePixelLocationMeasureGetPixelLocationFragment
            # for the minimap
            ...minimapControlsGetMeasureLayerStateFragment
            # for path
            ...pathMeasureGetMeasureLayerFragment
            # for focus in the path control
            ...focusMeasureGetMeasureLayerFragment
            # for the coordinates in the path control
            ...coordinateMeasureGetMeasureLayerFragment
            # for the closed path flag in the path control
            ...closeMeasureGetMeasureLayerFragment
            # for downloading the signal along the measure path
            ...profileMeasureGetMeasureLayerFragment
            # for the zoom control
            ...zoomControlsGetZoomStateFragment
            # for the viz control
            ...vizControlsGetViewFragment
        }
    }
`

// end of file
