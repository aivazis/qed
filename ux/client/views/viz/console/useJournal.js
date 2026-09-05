// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
import { journal } from './store'


// the records the console shows; subscribing keeps the stream open for the life of the caller
export const useJournal = () => {
    // read the buffer from the store, re-rendering on every change
    return React.useSyncExternalStore(journal.subscribe, journal.entries)
}


// end of file
