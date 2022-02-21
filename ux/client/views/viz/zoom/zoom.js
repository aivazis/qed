// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { SVG, Slider, Tray } from '~/widgets'

// locals
// hooks
import { useGetView } from '../viz/useGetView'
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
import { useSetZoomLevel } from '../viz/useSetZoomLevel'
// styles
import styles from './styles'


//  display the zoom control
export const Zoom = () => {
    // look up the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // make a handler that sets the zoom level
    const setZoom = useSetZoomLevel()
    // get the active view and unpack it
    const { reader, dataset, channel } = useGetView()

    // inspect the view components to initialize my state
    const enabled = reader && dataset && channel

    // set the zoom level range
    const [min, max] = [0, 4]
    // set up the tick marks
    const major = [...Array(max - min + 1).keys()].map((_, idx) => min + idx)
    // slider configuration
    const slider = {
        value: zoom, setValue: setZoom,
        min, max, major,
        direction: "row", labels: "bottom", arrow: "top",
        height: 50, width: 200,
    }

    // mix my paint
    const zoomPaint = styles.zoom(enabled ? "enabled" : "disabled")

    // and render
    return (
        <Tray title="zoom" initially={true} style={zoomPaint.tray}>
            {/* the control housing */}
            <Housing height={slider.height} width={slider.width}>
                {/* the slider */}
                <Controller enabled={enabled} {...slider} />
            </Housing>
        </Tray>
    )
}


// the slider housing
const Housing = styled(SVG)`
    margin: 1.0rem auto;
`


// the controller
const Controller = styled(Slider)`
`


// end of file
