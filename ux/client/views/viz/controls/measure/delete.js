// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X } from '~/shapes'

// local
// components
import { Button } from './button'


// remove this point from the path
export const Delete = ({ idx, point }) => {
    // render
    return (
        <Button>
            <X />
        </Button>
    )
}


// end of file
