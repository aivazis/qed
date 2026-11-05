// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useServerQueryLoader } from './useSyncWithServer'
// components
import { Version } from './version'


// display the server state
export const Ping = ({ style, standing, ...props }) => {
    // preload the query
    const [qref, getVersion] = useServerQueryLoader()
    // schedule the query loading
    React.useEffect(() => {
        // variables
        const variables = {}
        // network options
        const options = {
            fetchPolicy: "network-only",
        }
        // get the data once; the event stream keeps track of the server from then on
        getVersion(variables, options)
        // all done
        return
    }, [])
    // if this is the first time
    if (qref === null) {
        // render nothing
        return
    }
    // otherwise, build the component with the version info and return it
    return (
        <Version qref={qref} style={style} standing={standing} />
    )
}


// end of file
