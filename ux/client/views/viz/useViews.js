// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the registered views
export const useViews = () => {
    // grab the list of {views} from context
    const { views } = React.useContext(Context)
    // and return it
    return views
}


// end of file
