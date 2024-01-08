// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Dead } from './dead'


// kill the server
export const Stop = ({ base }) => {
    // ask the server to shut down
    fetch('stop').catch(
        // and swallow any errors
        () => null
    )
    // render the dead screen
    return (
        <Dead base={base} />
    )
}


// end of file
