// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the camera, which maps the pointer to diagram coordinates
import { useCamera } from '~/widgets/camera'

// local
// the editor
import { useEditDiagram } from './useEditDiagram'


// the media type of a factory dragged from the palette
export const factoryMediaType = "application/x-qed-factory"


// make the canvas a place to drop factories dragged from the palette; it lives inside the camera,
// which maps the drop point to diagram coordinates
export const Drops = ({ canvas }) => {
    // the map from the pointer to diagram coordinates, rounded onto the grid
    const { toICS } = useCamera()
    // the editor
    const { add } = useEditDiagram()
    // install the listeners on the canvas
    React.useEffect(() => {
        // get the canvas
        const target = canvas.current
        // if it is not there yet
        if (!target) {
            // there is nothing to do
            return
        }
        // a drag that carries a factory is welcome
        const over = evt => {
            // if it carries one
            if (evt.dataTransfer?.types?.includes(factoryMediaType)) {
                // say so
                evt.preventDefault()
                evt.dataTransfer.dropEffect = "copy"
            }
            // all done
            return
        }
        // a drop places the factory at the grid point under the pointer
        const drop = evt => {
            // get the family of the factory
            const family = evt.dataTransfer?.getData(factoryMediaType)
            // if there is none
            if (!family) {
                // this drop is not for me
                return
            }
            // otherwise, it is mine
            evt.preventDefault()
            // where it landed
            const { x, y } = toICS({ x: evt.clientX, y: evt.clientY })
            // place it
            add({ family, x, y })
            // all done
            return
        }
        // listen
        target.addEventListener("dragover", over)
        target.addEventListener("drop", drop)
        // and clean up
        return () => {
            target.removeEventListener("dragover", over)
            target.removeEventListener("drop", drop)
        }
    })
    // nothing to draw
    return null
}

// end of file
