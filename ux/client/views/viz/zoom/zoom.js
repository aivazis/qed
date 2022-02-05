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
// components
import { Controller } from './controller'
// styles
import styles from './styles'


// display the zoom control
export const Zoom = () => {
    const width = 200
    const height = 100
    const scale = width / 1000
    const place = `scale(${scale}) translate(0 0)`

    // set up my state
    const state = "enabled"
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
