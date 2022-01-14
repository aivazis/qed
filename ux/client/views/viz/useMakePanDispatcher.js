// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useSynced } from './useSynced'
import { usePanSharedCamera } from './usePanSharedCamera'


// get the viewport position
export const useMakePanDispatcher = (viewports) => {
    // get the sync registry
    const synced = useSynced()
    // and the shared camera controller
    const panSharedCamera = usePanSharedCamera()

    // make a handler that pans the shared camera and scrolls the synced viewports
    const pan = (evt, idx) => {
        // if i have a raised flag
        if (semaphores[idx] > 0) {
            // decrement the semaphore
            --semaphores[idx]
            // and bail
            return
        }
        // if i am not synced
        if (!synced[idx]) {
            // nothing to do
            return
        }
        // get the scrolling element
        const element = evt.target
        // get the scroll coordinates
        const y = Math.max(element.scrollTop, 0)
        const x = Math.max(element.scrollLeft, 0)
        // update the shared camera
        panSharedCamera({ x, y })
        // go through the viewports
        viewports.forEach((port, i) => {
            // if i bumped into myself or a viewport that isn't synced
            if (i === idx || !synced[i]) {
                // move on
                return
            }
            // everybody else gets a bump on its semaphore
            ++semaphores[i]
            // and scrolls to my location
            port.scroll(x, y)
            // all done
            return
        })
    }

    // make a pile of semaphores
    const semaphores = Array(viewports.length).fill(0)
    // and a handler wrapper
    const dispatch = idx => evt => pan(evt, idx)

    // and return it
    return dispatch
}


// end of file
