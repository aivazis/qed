// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Note } from './note'
import { Ping } from './ping'


// display the server state
export const Server = ({ style, ...props }) => {
    // build the component with the version info and return it
    return (
        <React.Suspense fallback={<Note style={style} />}>
            <Ping style={style} />
        </React.Suspense>
    )
}


// end of file
