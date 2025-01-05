// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useServerQueryLoader } from './useSyncWithServer'
// components
import { Version } from './version'


// display the server state
export const Ping = ({ style, ...props }) => {
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
        // get the data immediately
        getVersion(variables, options)
        // and schedule a recurring refresh
        // const timer = setInterval(getVersion, 1000, variables, options)
        // return the cleanup function
        return () => {
            // disable the timer
            // clearInterval(timer)
            // all done
            return
        }
    }, [])
    // if this is the first time
    if (qref === null) {
        // render nothing
        return
    }
    // otherwise, build the component with the version info and return it
    return (
        <Version qref={qref} style={style} />
    )
}


// end of file
