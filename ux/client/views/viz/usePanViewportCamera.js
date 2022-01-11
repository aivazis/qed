// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { ViewportContext } from './viewportContext'


// get the viewport position
export const usePanViewportCamera = (viewport) => {
    // grab the position mutator
    const { setPosition } = React.useContext(ViewportContext)

    // make handler for the scroll event
    const pan = (evt) => {
        // get the scrolling viewport
        const target = evt.target
        // interpret the scroll info as the coordinates of the viewport camera
        const x = Math.max(target.scrollLeft, 0)
        const y = Math.max(target.scrollTop, 0)
        // update the viewport camera
        setPosition((old) => {
            // if this is not a substantive update
            if (old.x === x && old.y === y) {
                // bail
                return old
            }

            // otherwise, build the new camera position
            const position = { ...old, x, y }
            // and return it
            return position
        })

        // all done
        return
    }

    // and return it
    return pan
}


// end of file
