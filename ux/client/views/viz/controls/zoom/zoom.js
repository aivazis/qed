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
export const Zoom = ({ min = 0, max = 4 }) => {
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

    // set up the tick marks
    const major = [...Array(max - min + 1).keys()].map((_, idx) => min + idx)
    // slider configuration
    const xSlider = {
        value: zoom, setValue: setZoom,
        min, max, major,
        direction: "row", labels: "top", arrows: "bottom",
        height: 100, width: 200,
    }
    const ySlider = {
        value: zoom, setValue: setZoom,
        min, max, major,
        direction: "column", flipped: true, labels: "right", arrows: "left",
        height: 200, width: 100,
    }

    const width = ySlider.width + xSlider.width
    const height = ySlider.height + xSlider.height - 40

    // mix my paint
    const state = enabled ? "enabled" : "disabled"

    // and render
    return (
        <Tray title="zoom" initially={true} state={state} scale={0.5}>
            {/* the control housing */}
            <Housing height={height} width={width}>
                {/* the vertical slider */}
                <g transform="translate(-20 0)">
                    <Controller enabled={enabled} {...ySlider} />
                </g>
                {/* the horizontal slider */}
                <g transform="translate(60 180)">
                    <Controller enabled={enabled} {...xSlider} />
                </g>
                {/* the minimap */}
                <g transform="translate(60 0) scale(200)">
                    <Minimap zoom={zoom} shape={dataset.shape} />
                </g>
                {/* the lock */}
                <g transform="translate(30 230)">
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
