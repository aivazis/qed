// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Target } from '~/shapes'

// local
// components
import { Button } from './button'


// locate the given point on the viewport
export const Focus = ({ idx, point }) => {
    // render
    return (
        <Button>
            <Target />
        </Button>
    )
}


// end of file
