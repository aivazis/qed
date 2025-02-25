// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useMakeBox } from '~/views/viz/measure'
// shapes
import { Square } from '~/shapes'

// local
// components
import { Button } from './button'


// make a box out of a pair of anchors
export const Rect = ({ viewport }) => {
    // get the path mutator that turns a pair of anchors into a box
    const { box } = useMakeBox(viewport)

    // build the handler
    const rect = () => {
        // build a rectangle out of the existing anchors
        box()
        // and done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: rect,
        // marked on the icon that takes the click, so drivers can find and press it
        role: "button",
        "aria-label": "make a box out of the two anchors",
    }

    // render
    return (
        <Button behaviors={behaviors}>
            <Square />
        </Button>
    )
}


// end of file
