// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// local
// hooks
import { useViewports } from './useViewports'


// make a handler that centers a viewport at a given point
export const useCenterViewport = (viewport = null) => {
    // get the table of viewports and the active viewport so we can use it as a fall back
    const { activeViewport, viewports } = useViewports()
    // normalize the viewport
    viewport ??= activeViewport

    // make a handler that scrolls the viewport so that the given point is at the center
    const center = ({ x, y }) => {
        // get the scrolling container
        const placemat = viewports[viewport]
        // measure it
        const box = placemat.getBoundingClientRect()
        // extract the viewport size
        const width = box.width
        const height = box.height
        // compute the new position of the upper left hand corner
        const left = x - width / 2
        const top = y - height / 2
        // scroll there
        placemat.scroll({ left, top, behavior: "smooth" })
        // all done
        return
    }

    // and return it
    return center
}


// end of file
