// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the current detail level
export const useDetail = () => {
    // grab the current detail level
    const { detail, setDetail } = React.useContext(Context)
    // and return it
    return { detail, setDetail }
}


// end of file
