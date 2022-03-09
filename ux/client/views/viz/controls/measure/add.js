// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Plus } from '~/shapes'

// local
// components
import { Button } from './button'


// insert a point to the path after the given one
export const Add = ({ idx, point }) => {
    // render
    return (
        <Button>
            <Plus />
        </Button>
    )
}


// end of file
