// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { SVG, Slider, Tray } from '~/widgets'

// locals
// hooks
import { useGetView } from '../../viz/useGetView'
import { useGetZoomLevel } from '../../viz/useGetZoomLevel'
import { useSetZoomLevel } from '../../viz/useSetZoomLevel'
// components
import { Lock } from './lock'
import { Minimap } from './minimap'


//  display the zoom control
export const Zoom = ({ min = -4, max = 4 }) => {
    // set the scale
    const ils = 200
    // the lock button state
    const [lock, setLock] = React.useState(true)
    // look up the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // make a handler that sets the zoom level
    const setZoom = useSetZoomLevel()
    // get the active view and unpack it
    const { reader, dataset, channel } = useGetView()

    // make the zoom lock toggle
    const toggle = () => {
        // toggle the state
        setLock(old => !old)
        // all done
        return
    }
    // inspect the view components to initialize my state
    const enabled = (reader && dataset && channel) ? true : false

    // adjust the horizontal zoom
    const setHorizontalZoom = value => {
        // build the new value
        const level = { horizontal: value, vertical: lock ? value : zoom.vertical }
        // and set it
        setZoom(level)
        // all done
        return
    }
    // adjust the vertical zoom
    const setVerticalZoom = value => {
        // build the new value
        const level = { vertical: value, horizontal: lock ? value : zoom.horizontal }
        // and set it
        setZoom(level)
        // all done
        return
    }

    // set up the tick marks
    const major = [...Array((max - min) / 2 + 1).keys()].map((_, idx) => min + 2 * idx)
    const minor = [...Array((max - min) / 2).keys()].map((_, idx) => min + 1 + 2 * idx)
    // slider configuration
    const xSlider = {
        value: zoom.horizontal, setValue: setHorizontalZoom,
        min, max, major, minor, precision: 0,
        direction: "row", labels: "top", arrows: "bottom", markers: true,
        height: ils / 2, width: ils,
    }
    const ySlider = {
        value: zoom.vertical, setValue: setVerticalZoom,
        min, max, major, minor, precision: 0,
        direction: "column", flipped: true, labels: "right", arrows: "left", markers: true,
        height: ils, width: ils / 2,
    }
    // set up the overall dimensions of the control
    const width = 340
    const height = 290

    // mix my paint
    const state = enabled ? "enabled" : "disabled"
    // and render
    return (
        <Tray title="zoom" initially={true} state={state} scale={0.5}>
            {/* the control housing */}
            <Housing height={height} width={width}>
                {/* the vertical slider */}
                <g transform="translate(10 0)">
                    <Controller enabled={enabled} {...ySlider} />
                </g>
                {/* the horizontal slider */}
                <g transform="translate(100 190)">
                    <Controller enabled={enabled} {...xSlider} />
                </g>
                {/* the minimap */}
                <g transform={`translate(100 0) scale(${ils})`}>
                    <Minimap ils={ils} zoom={zoom} shape={dataset.shape} />
                </g>
                {/* the lock */}
                <g transform="translate(60 240)">
                    <Lock lock={lock} toggle={toggle} />
                </g>
            </Housing>
        </Tray>
    )
}


// the slider housing
const Housing = styled(SVG)`
    margin: 1.0rem auto;
`

// the controllers
const Controller = styled(Slider)`
`

// end of file
