// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the store the event stream reports to; imported by path, since the package that holds it
// publishes the automation surface, which reaches most of the client
import { reachability } from '~/automation/reachability'


// subscribe to whether this client is in touch with its server
export const useReachability = () => {
    // read the store, re-rendering whenever the standing changes
    return React.useSyncExternalStore(reachability.subscribe, reachability.state)
}


// end of file
