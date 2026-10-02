// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the tile loader: a tile carries its address in {data-src}, and the loader copies it into {src}
// once the tile comes within {margin} of the visible part of the box that scrolls it, so only the
// tiles on the screen, and a thin ring around them, are fetched
//
// every tile it fetches is announced with a {tilefetch} event that bubbles up from the image, so
// whoever keeps track of the traffic of a view learns about exactly the tiles that are on their
// way, and can expect a {load} or an {error} for each one

// the distance past the visible part of its scroller at which a tile is fetched, in pixels: a
// quarter of a tile keeps the tiles that scroll into view during a pan from showing up blank,
// which fetching only the visible ones does not, and costs a couple of tiles per screen
const margin = 128

// an observer for each scroller, created the first time one of its tiles is observed
const observers = new WeakMap()
// the observer of tiles that scroll with the document itself
let documentObserver = null


// find the nearest ancestor of {element} that scrolls its contents
const scrollerOf = element => {
    // start with the parent
    let node = element.parentElement
    // and climb
    while (node !== null) {
        // get the overflow policy of this node
        const { overflowX, overflowY } = window.getComputedStyle(node)
        // a node that scrolls along either axis
        if (/(auto|scroll)/.test(overflowX + overflowY)) {
            // is the one
            return node
        }
        // otherwise, keep climbing
        node = node.parentElement
    }
    // no ancestor scrolls, so the tile scrolls with the document
    return null
}


// fetch the tiles that came within reach
const reach = entries => {
    // go through the tiles whose visibility changed
    for (const entry of entries) {
        // the ones that are out of reach
        if (!entry.isIntersecting) {
            // wait
            continue
        }
        // the others get fetched
        fetchTile(entry.target)
    }
    // all done
    return
}


// copy the address of {image} into its {src}, unless it is already there
const fetchTile = image => {
    // the address the tile should show
    const address = image.getAttribute("data-src")
    // a tile without one, or one that already shows it
    if (!address || image.getAttribute("src") === address) {
        // has nothing to fetch
        return
    }
    // announce the fetch, so it can be waited on
    image.dispatchEvent(new Event("tilefetch", { bubbles: true }))
    // and start it
    image.setAttribute("src", address)
    // all done
    return
}


// get the observer for the tiles scrolled by {scroller}, making it the first time
const observerOf = scroller => {
    // tiles that scroll with the document
    if (scroller === null) {
        // share the document observer
        if (documentObserver === null) {
            // making it on first use
            documentObserver = new IntersectionObserver(reach, { rootMargin: `${margin}px` })
        }
        // and hand it back
        return documentObserver
    }
    // look up the observer of this scroller
    let observer = observers.get(scroller)
    // make one, if there isn't one
    if (!observer) {
        // over the visible part of the scroller, grown by the margin
        observer = new IntersectionObserver(reach, { root: scroller, rootMargin: `${margin}px` })
        // and remember it
        observers.set(scroller, observer)
    }
    // hand it back
    return observer
}


// start watching {image}; an image that is watched already is looked at again, which is how a
// tile whose address changed gets the new one fetched when it is within reach
export const watch = image => {
    // the observer of its scroller
    const observer = observerOf(scrollerOf(image))
    // stop watching, so the observer looks at it afresh
    observer.unobserve(image)
    // and watch it again; the observer reports on it right away
    observer.observe(image)
    // hand back the way to stop
    return () => observer.unobserve(image)
}


// end of file
