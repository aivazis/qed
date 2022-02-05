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
// hooks
import { useGetView } from '../viz/useGetView'
// components
import { Controller } from './controller'
// styles
import styles from './styles'


// display the zoom control
export const Zoom = () => {
    // get the active view and unpack it
    const { reader, dataset, channel } = useGetView()

    // check the view components and initialize my state
    const state = (!reader || !dataset || !channel) ? "disabled" : "enabled"

    // set a length scale
    const width = 200
    // use it to derive the height of the control
    const height = width / 2
    // the control draws itself in a logical box of width {1000}
    const scale = width / 1000
    // build the transform that sizes and positions te control
    const place = `scale(${scale}) translate(0 0)`


    // mix my paint
    const zoomPaint = styles.zoom(state)
    const controllerPaint = styles.controller

    // and render
    return (
        <Tray title="zoom" initially={true} style={zoomPaint.tray}>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                width={width} height={height} style={controllerPaint.box}>
                <g transform={place}>
                    <Controller state={state} />
                </g>
            </svg>
        </Tray>
    )
}


// end of file
