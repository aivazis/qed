// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the zoom level of the active viewport
export const useSetZoomLevel = () => {
    // grab the active viewport, the table of synced views,  and the zoom level table mutator
    const { viewports, activeViewport, synced, setZoom } = React.useContext(Context)

    // a handler that sets the zoom level of the active viewport
    const set = value => {
        // update the zoom table
        setZoom(old => {
            // make a copy of the old table
            const table = [...old]
            // adjust the entry that corresponds to the active view
            table[activeViewport] = value

            // if the active port is synced
            if (synced[activeViewport].zoom) {
                // go through all the views in the sync table
                synced.forEach((status, viewport) => {
                    // find the synced ones
                    if (status.zoom) {
                        // and adjust their zoom level as well
                        table[viewport] = value
                    }
                })
            }

            // get the viewport
            const viewport = viewports.current[activeViewport]
            // measure it
            const { scrollLeft, clientWidth, scrollTop, clientHeight } = viewport

            // get the old zoom
            const oldZoom = old[activeViewport]
            // and the new one
            const newZoom = table[activeViewport]
            // compute the magnification factors
            const mH = 2 ** -(oldZoom.horizontal - newZoom.horizontal)
            const mV = 2 ** -(oldZoom.vertical - newZoom.vertical)

            // compute the new scroll location so the center pixel remains the same after zoom
            const top = mV * (scrollTop + clientHeight / 2) - clientHeight / 2
            const left = mH * (scrollLeft + clientWidth / 2) - clientWidth / 2

            // scroll there
            viewport.scroll(left, top)

            // return the new table
            return table
        })

        // all done
        return
    }

    // return the handler
    return set
}


// end of file
