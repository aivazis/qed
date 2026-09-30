// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the tiles each viewport is waiting for, and a way to wait until they have arrived
//
// a change to a controller of a view invalidates every tile it shows, so a client that sends the
// next change before the tiles of the last one have arrived asks the server for screens nobody
// will see; the controllers use {quiet} to pace their updates by the screen instead

// the tiles each viewport is waiting for, as a map from the viewport to the set of its images
const waiting = new Map()
// whether the listeners are in place
let listening = false


// find the viewport an element belongs to
const viewportOf = element => {
    // look for the box of the viewport among the ancestors of the element
    const box = element.closest ? element.closest("[data-qed-viewport]") : null
    // an element outside any viewport belongs to none
    if (box === null) {
        // so say so
        return null
    }
    // otherwise, read the index of the viewport off its box
    return Number(box.getAttribute("data-qed-viewport"))
}


// check whether an element is a tile
const isTile = element => (
    // tiles are images that say so
    element && element.getAttribute && element.getAttribute("data-pyre-widget") === "tile"
)


// a tile is about to be fetched
const unveil = evt => {
    // get the image
    const image = evt.target
    // anything other than a tile
    if (!isTile(image)) {
        // is none of my business
        return
    }
    // find its viewport
    const viewport = viewportOf(image)
    // a tile outside any viewport
    if (viewport === null) {
        // is none of my business either
        return
    }
    // make room for the viewport, if this is its first tile
    if (!waiting.has(viewport)) {
        // with an empty set
        waiting.set(viewport, new Set())
    }
    // and note that the viewport is waiting for this tile
    waiting.get(viewport).add(image)
    // all done
    return
}


// a tile has arrived, or failed to
const arrive = evt => {
    // get the image
    const image = evt.target
    // anything other than a tile
    if (!isTile(image)) {
        // is none of my business
        return
    }
    // go through the viewports
    for (const images of waiting.values()) {
        // and stop waiting for this tile in whichever one was
        images.delete(image)
    }
    // all done
    return
}


// start watching the tiles, once
export const listen = () => {
    // if the listeners are in place
    if (listening) {
        // there is nothing to do
        return
    }
    // the tile loader announces each tile it is about to fetch
    document.addEventListener("tilefetch", unveil, true)
    // an image announces its arrival, and its failure, to listeners that capture it, since these
    // events do not bubble
    document.addEventListener("load", arrive, true)
    document.addEventListener("error", arrive, true)
    // and remember they are in place
    listening = true
    // all done
    return
}


// count the tiles a viewport is waiting for
const pending = viewport => {
    // get the tiles of the viewport
    const images = waiting.get(viewport)
    // a viewport that never waited for anything
    if (!images) {
        // is waiting for nothing
        return 0
    }
    // go through them
    for (const image of images) {
        // an image that left the page will never arrive
        if (!image.isConnected) {
            // so stop waiting for it
            images.delete(image)
        }
    }
    // and count the rest
    return images.size
}


// wait until the tiles of a viewport have arrived, but no longer than {cap} milliseconds
export const quiet = (viewport, cap = 1000) => new Promise(resolve => {
    // note when the wait started
    const start = performance.now()
    // and count the frames, since the tiles of a change start on the frames after it
    let frames = 0
    // check on the tiles, once a frame
    const check = () => {
        // one more frame
        frames += 1
        // once the tiles of the change have had the chance to start, and have all arrived
        if (frames > 2 && pending(viewport) === 0) {
            // the wait is over
            return resolve()
        }
        // if the wait has gone on long enough
        if (performance.now() - start >= cap) {
            // it is over too
            return resolve()
        }
        // otherwise, check again on the next frame
        requestAnimationFrame(check)
        // all done
        return
    }
    // start checking on the next frame
    requestAnimationFrame(check)
})


// end of file
