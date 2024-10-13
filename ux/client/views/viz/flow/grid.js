// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useCamera } from '~/widgets/camera'
// local
import styles from './styles'


// highlight the grid cell that's under the cursor
// N.B.: this component renders whenever either the cursor position or the camera changes
//       - on mouse move, we highlight the current cell
//       - on camera changes, we hide the highlight; it will show up next time the cursor moves
export const Grid = () => {
    // get the current camera and cursor position
    const { camera, cursor } = useCamera()
    // set aside some storage so we can remember the previous values
    const ref = React.useRef(camera)
    // get the camera setting from our last render
    const prevCamera = ref.current
    // decide whether we should highlight the current cell
    const highlight = (cursor !== null) && (camera === prevCamera)
    // record the new camera settings
    ref.current = camera

    // if we are not highlighting
    if (!highlight) {
        // there is nothing to render
        return null
    }

    // otherwise, unpack the cursor location
    const { x, y } = cursor
    // and make a mark; don't forget we are in a quarter cell grid, so the highlight marks
    // the four grid cells around the current coordinate
    return (
        <rect x={x - 1} y={y - 1} width={2} height={2} style={styles.cell} />
    )
}


// end of file
