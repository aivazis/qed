// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get the viewport position
export const useMakePanDispatcher = ({ synced, zooms, viewports }) => {
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
        // scroll offsets live in *rendered* pixels, which scale as 2**zoom; convert mine to source
        // pixels -- zoom-independent, hence comparable to a viewport at any other zoom level
        const [myH, myV] = [zooms[idx]?.horizontal ?? 0, zooms[idx]?.vertical ?? 0]
        const x = Math.max(element.scrollLeft, 0) * 2 ** -myH
        const y = Math.max(element.scrollTop, 0) * 2 ** -myV
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
            // shift by the relative (source-pixel) offset, then convert into the peer's own
            // rendered pixels, so the same source pixel lines up regardless of its zoom
            const [h, v] = [zooms[i]?.horizontal ?? 0, zooms[i]?.vertical ?? 0]
            port.scroll(
                (x + sync.offsets.x - mySync.offsets.x) * 2 ** h,
                (y + sync.offsets.y - mySync.offsets.y) * 2 ** v
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
