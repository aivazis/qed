// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
    // get the path mutator that can split a segment in two
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
    }

    // render
    return (
        <Button behaviors={behaviors}>
            <Square />
        </Button>
    )
}


// end of file
