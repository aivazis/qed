// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Tray } from '~/widgets'

// locals
// support
import { dimensions } from './dimensions'
// hooks
import { useGetView } from '../viz/useGetView'
// components
import { Controller } from './controller'
// styles
import styles from './styles'


// display the zoom control
export const Zoom = () => {
    // build a ref for my container
    const ref = React.useRef()
    // get the active view and unpack it
    const { reader, dataset, channel } = useGetView()

    // inspect the view components to initialize my state
    const state = (!reader || !dataset || !channel) ? "disabled" : "enabled"


    // build the control geometry
    const geometry = dimensions({
        // the minimum zoom level
        min: 0,
        // the maximum zoom level
        max: 4,
        // dimensions
        height: 50,
        width: 200,
    })

    // mix my paint
    const zoomPaint = styles.zoom(state)
    const controllerPaint = styles.controller

    // and render
    return (
        <Tray title="zoom" initially={true} style={zoomPaint.tray}>
            {/* the control housing */}
            <svg ref={ref} version="1.1" xmlns="http://www.w3.org/2000/svg"
                width={geometry.width} height={geometry.height}
                style={controllerPaint}>

                {/* the controller engine */}
                <Controller geometry={geometry} state={state} />

            </svg>

        </Tray >
    )
}


// end of file
