// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useEvent } from '~/hooks'

// local
// hooks
import { useZooming } from './useZooming'
import { useEndZooming } from './useEndZooming'
import { useSetZoomLevel } from '../viz/useSetZoomLevel'


// null component that installs event listeners that handle the movement of the indicator
export const Behaviors = ({ geometry, client }) => {
    // get the zooming flag
    const zooming = useZooming()
    // make the handler that clears the zooming flag
    const endZooming = useEndZooming()
    // make a handler that sets the zoom level
    const setZoom = useSetZoomLevel()

    // unpack the geometry
    const { viewportToUser } = geometry

    // when the mouse moves
    const move = (evt) => {
        // if the indicator is not being dragged
        if (!zooming) {
            // bail
            return
        }
        // get the controller bounding box
        // N.B.: MDN has a warning against spreading this result, so do it in two steps
        //       even though it's my experience that this works
        const box = client.current.getBoundingClientRect()
        // grab the coordinates of its left edge
        const left = box.left
        // transform the mouse coordinates into controller coordinates
        const zoom = viewportToUser(evt.clientX - left)
        // adjust the zoom level
        setZoom(zoom)
        // all done
        return
    }

    // install the listeners
    useEvent({
        name: "mouseup", listener: endZooming, client,
        triggers: []
    })

    useEvent({
        name: "mousemove", listener: move, client,
        triggers: [zooming, setZoom],
    })

    useEvent({
        name: "mouseleave", listener: endZooming, client,
        triggers: [],
    })


    // leave nothing behind
    return null
}


// end of file
