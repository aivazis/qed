// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
import { reachability } from './reachability'


// subscribe to whether this client is in touch with its server
export const useReachability = () => {
    // read the store, re-rendering whenever the standing changes
    return React.useSyncExternalStore(reachability.subscribe, reachability.state)
}


// end of file
