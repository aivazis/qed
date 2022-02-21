// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

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

    // level range
    const [min, max] = [0, 4]
    // slider configuration
    const slideConf = {
        value: zoom, setValue: setZoom,
        direction: "row", labels: "bottom", arrow: "top",
        height: 50, width: 200,
        min, max, major: [...Array(max - min + 1).keys()].map((_, idx) => min + idx)
    }

    // mix my paint
    const zoomPaint = styles.zoom(enabled ? "enabled" : "disabled")
    const controllerPaint = styles.controller

    // and render
    return (
        <Tray title="zoom" initially={true} style={zoomPaint.tray}>
            {/* the control housing */}
            <SVG height={50} width={200} style={controllerPaint}>
                {/* the slider */}
                <Slider enabled={enabled} {...slideConf} />
            </SVG>
        </Tray>
    )
}


// end of file
