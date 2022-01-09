// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './context'


// viewport registration
export const useRegisterViewport = (inSync = false) => {
    // make a reference for this viewport
    const viewport = React.useRef()
    // grab the sync table mutator from the context
    const { setSynced } = React.useContext(VizContext)

    // a handler that registers this viewport when the component that manages it mounts
    const register = () => {
        // update the sync table
        setSynced(old => {
            // make a copy of the old table
            const table = new Map(old)
            // add the new viewport with a default state
            table.set(viewport, inSync)
            // return the new table
            return table
        })
        // all done
        return
    }

    // a handler that removes a viewport from the sync table
    const unregister = () => {
        // update the sync table
        setSynced(old => {
            // make a copy of the current pile
            const table = new Map(old)
            // remove this viewport
            table.delete(viewport)
            // return the new state
            return table
        })
        // all done
        return
    }

    // schedule the effect
    React.useEffect(() => {
        // on mount, register the viewport
        register()
        // and return a cleanup
        return unregister
    }, []) // no triggers implies a mount/dismount effect

    // return the viewport ref
    return viewport
}


// end of file
