// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
// locals
// context
import { Context } from './context'


// flex support
export const useTopic = () => {
    // grab the state and its mutator
    const { topic, setTopic } = React.useContext(Context)

    // the state managers
    const pick = newTopic => setTopic(newTopic)

    // build and return the context relevant to the activity panel
    return {
        // the flag
        topic,
        // and the selector
        pick,
    }
}


// end of file
