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

    // make a handler that swallows events until a semaphore is raised
    const debounce = (_, idx) => {
        // decrement the semaphore
        --semaphores[idx]
        // if the flag is cleared
        if (semaphores[idx] == 0) {
            // reset back to normal behaviors
            scrollers[idx] = pan
        }
        // all done
        return
    }
    // and one that pans the shared camera and scrolls the synced viewports
    const pan = (evt, idx) => {
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
            // everybody else gets the {debounce} handler installed
            scrollers[i] = debounce
            // a bump on its semaphore
            ++semaphores[i]
            // and scrolls to my location
            port.scroll(x, y)
            // all done
            return
        })
    }

    // make a pile of semaphores
    const semaphores = Array(viewports.length).fill(0)
    // a table of of event handlers
    const scrollers = semaphores.map((_, idx) => synced[idx] ? pan : noop)
    // and a handler wrapper
    const dispatch = idx => evt => scrollers[idx](evt, idx)

    // and return it
    return dispatch
}


// a noop event handler
const noop = () => { }


// end of file
