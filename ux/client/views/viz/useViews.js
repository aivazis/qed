// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './context'


// access to the registered views
export const useViews = () => {
    // grab the list of {views} from context
    const { views, activeView } = React.useContext(VizContext)
    // and return it
    return { views, activeView }
}


// end of file
