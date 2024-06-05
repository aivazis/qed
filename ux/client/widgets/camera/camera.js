// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// hooks
import { useCamera } from './useCamera'
// paint
import styles from './styles'


// a passive transformation to the intrinsic coordinate system (ICS) of the diagram
const Lens = ({ style, children }) => {
    // the camera factory
    const { els, camera } = useCamera()
    // unpack the camera parameters
    const { x, y, z, phi } = camera
    // transform to viewport coordinates
    const vx = els * x
    const vy = els * y
    const vz = els / z
    // pan
    const pan = `translate(${vx} ${vy})`
    // zoom
    const zoom = `scale(${vz})`
    // orient
    const twist = `rotate(${phi})`
    // assemble the transform
    const pov = [pan, zoom, twist].join(" ")
    // mix my paint
    const paint = { ...styles, ...style }
    // render
    return (
        <g transform={pov} style={paint}>
            {children}
        </g>
    )
}


// assemble the camera
export const Camera = React.forwardRef(({ viewport, scale = 25, style, children }, viewRef) => {
    // set up the context provider and install the lens
    return (
        <Provider ref={viewRef} viewport={viewport} scale={scale}>
            <Lens style={style}>
                {children}
            </Lens>
        </Provider>
    )
})


// end of file
