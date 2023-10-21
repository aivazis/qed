// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
// locals
import { dead as deadPaint } from './styles'


// the area
export const Dead = () => {
    // the container
    return (
        <section style={deadPaint.stop}>
            <div style={deadPaint.placeholder}>
                <a href="/" style={deadPaint.link}>qed</a>
                &nbsp;has shut down; please close this window
            </div>
        </section>
    )
}


// end of file
