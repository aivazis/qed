// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the current focus
export const useFocus = () => {
    // get the current focus
    const { focus } = React.useContext(Context)
    // and return it
    return focus
}


// end of file
