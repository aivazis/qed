// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// locals
// context
import { Context } from './context'


// flex support
export const useActivityPanel = () => {
    // grab the state and its mutator
    const { activityPanel, setActivityPanel } = React.useContext(Context)

    // the state managers
    const showActivityPanel = () => { setActivityPanel(true) }
    const hideActivityPanel = () => { setActivityPanel(false) }
    const toggleActivityPanel = () => { setActivityPanel(old => !old) }

    // build and return the context relevant to the activity panel
    return {
        // the flag
        activityPanel,
        // and its mutators
        showActivityPanel, hideActivityPanel, toggleActivityPanel,
    }
}


// end of file
