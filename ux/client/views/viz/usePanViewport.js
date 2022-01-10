// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { ViewportContext } from './viewportContext'
// hooks
import { useGetSyncRegistry } from './useGetSyncRegistry'


// get the viewport position
export const usePanViewport = (viewport) => {
    // grab the position mutator
    const { setPosition } = React.useContext(ViewportContext)
    // and the scrolling flag and its mutator
    // the viewport sync table
    const syncRegistry = useGetSyncRegistry()

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

            // find out whether this viewport camera is synced to the shared one
            const synced = syncRegistry.get(viewport)
            // and if so
            if (synced) {
                // go though all the registered viewports
                syncRegistry.forEach((flag, port) => {
                    // this viewport and viewports that are not synced
                    if (port === viewport || !flag) {
                        // get skipped
                        return
                    }
                    // for the rest, grab their underlying element and adjust its scroll position
                    port.current?.scrollTo({ left: x, top: y, behavior: "instant" })
                    // all done
                    return
                })
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
