// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the mapping between the scroll position of a viewport and the source pixel at its center
import { centerOf, lookAtCenter } from '../viewer/viewport'


// get the viewport position
export const useMakePanDispatcher = ({ synced, viewports }) => {
    // make a handler that pans the shared camera and scrolls the synced viewports
    const pan = (evt, idx) => {
        // get the scrolling element
        const element = evt.target
        // the panel hears the scrolls of everything in it; only those of the viewport itself move
        // its peers
        if (element !== viewports[idx]) {
            // so leave the rest alone
            return
        }
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
        // the source pixel at my center; centers, unlike scroll offsets, mean the same place in
        // viewports of any size and zoom, which is what the server keeps in step as well
        const here = centerOf(element)
        // go through the viewports
        viewports.forEach((port, i) => {
            // get the sync state
            const sync = synced[i]
            // if i bumped into myself, a viewport that isn't synced, or one that isn't up yet
            if (i === idx || !sync?.scroll || !port) {
                // move on
                return
            }
            // remember where the peer is
            const [left, top] = [port.scrollLeft, port.scrollTop]
            // look at my center, shifted by the difference of our offsets: columns by x, rows by y
            lookAtCenter(port, {
                row: here.row + sync.offsets.y - mySync.offsets.y,
                col: here.col + sync.offsets.x - mySync.offsets.x,
            })
            // a peer that was already there gets no scroll event, so there is nothing to suppress
            if (port.scrollLeft === left && port.scrollTop === top) {
                // move on
                return
            }
            // otherwise, its scroll is mine: bump its semaphore, so it doesn't move the others
            ++semaphores[i]
            // and leave a note of where it landed, so it doesn't report the move to the server
            port.qedFollowing = centerOf(port)
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
