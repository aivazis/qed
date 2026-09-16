// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// styles
import { failure as paintFailure } from './styles'


// the reason a folder could not be listed
export const Failure = ({ reason }) => {
    // render
    return (
        <div style={paintFailure} title={reason}>
            {reason}
        </div>
    )
}


// end of file
