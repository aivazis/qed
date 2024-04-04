// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Plus } from '~/shapes'

// local
// hooks
import { useAnchorSplit } from '~/views/viz/measure'
// components
import { Button } from './button'


// insert a point to the path after the given one
export const Add = ({ viewport, idx }) => {
    // get the path mutator that can split a segment in two
    const { split } = useAnchorSplit(viewport)

    // build the handler
    const add = () => {
        // split my node
        split({ anchor: idx })
        // and done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: add,
    }

    // render
    return (
        <Button behaviors={behaviors}>
            <Plus />
        </Button>
    )
}


// end of file
