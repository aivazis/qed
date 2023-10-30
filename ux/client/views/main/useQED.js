// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useQED = () => {
    // grab the list of {views} from context
    const { qed } = React.useContext(Context)
    // and return it
    return { qed }
}


// end of file
