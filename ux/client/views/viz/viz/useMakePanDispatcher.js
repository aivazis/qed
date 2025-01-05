// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get the viewport position
export const useMakePanDispatcher = ({ synced, viewports }) => {
    // make a handler that pans the shared camera and scrolls the synced viewports
    const pan = (evt, idx) => {
        // if i have a raised flag
        if (semaphores[idx] > 0) {
            // decrement the semaphore
            --semaphores[idx]
            // and bail
            return
        }
        // get my state
        const mySync = synced[idx]
        // if i am not synced
        if (!mySync.scroll) {
            // nothing to do
            return
        }
        // get the scrolling element
        const element = evt.target
        // get the scroll coordinates
        const y = Math.max(element.scrollTop, 0)
        const x = Math.max(element.scrollLeft, 0)
        // go through the viewports
        viewports.forEach((port, i) => {
            // get the sync state
            const sync = synced[i]
            // if i bumped into myself or a viewport that isn't synced
            if (i === idx || !sync?.scroll) {
                // move on
                return
            }
            // everybody else gets a bump on its semaphore
            ++semaphores[i]
            // and scrolls to my location
            port.scroll(
                x + sync.offsets.x - mySync.offsets.x,
                y + sync.offsets.y - mySync.offsets.y
            )
            // all done
            return
        })
        // all done
        return
    }

    // make a pile of semaphores
    const semaphores = Array(viewports.length).fill(0)
    // and a handler wrapper
    const dispatch = idx => evt => pan(evt, idx)

    // and return it
    return { dispatch }
}


// end of file
