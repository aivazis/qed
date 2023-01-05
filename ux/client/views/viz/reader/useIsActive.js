// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the viewport sync registry
export const useIsActive = () => {
    // grab the activation state ref
    const { active } = React.useContext(Context)
    // and return its current value
    return active.current
}


// end of file
