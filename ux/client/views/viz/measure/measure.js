// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { SVG } from '~/widgets'

// locals
// context
import { Provider } from './context'
// components
import { Mark } from './mark'
import { Path } from './path'
// styles
import styles from './styles'


// the layer
export const Measure = (props) => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Panel {...props} />
        </Provider>
    )
}


// the panel renderer
const Panel = ({ shape, raster, zoom }) => {
    // storage for my collection of points
    const [points, setPoints] = React.useState([])

    // convert the zoom level to a scaling factor
    const scale = 2 ** zoom
    // and project the points back into screen coordinates
    const projected = points.map(point => point.map(coord => Math.trunc(coord / scale)))


    // add a point to the pile
    const pick = evt => {
        // check the status of the shift key
        const { shiftKey } = evt
        // if not pressed
        if (!shiftKey) {
            // bail
            return
        }
        // unpack the mouse coordinates relative to ULC of the client area
        const { offsetX, offsetY } = evt.nativeEvent
        // scale and pack
        const p = [scale * offsetX, scale * offsetY]
        // add to my pile
        setPoints(old => {
            // make a copy
            const pile = [...old]
            // add the new point to it
            pile.push(p)
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // controllers
    const behaviors = {
        onClick: pick,
    }

    // mix my paint
    const paint = styles.measure(raster)
    // and render
    return (
        <SVG style={paint} {...behaviors} >
            {/* join the points with a line */}
            <Path points={projected} />
            {/* and highlight them */}
            {projected.map((point, idx) => {
                // render a circle
                return <Mark key={idx} idx={idx} at={point} />
            })}
        </SVG>
    )
}


// end of file
