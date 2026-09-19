// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
// project
// shapes
import { Refresh as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { useRefreshArchive } from './useRefreshArchive'
// styles
import { refresh as paintRefresh } from './styles'


// control to list every folder on display of a data archive again
export const Refresh = ({ uri }) => {
    // get the refresher
    const refreshArchive = useRefreshArchive()
    // build the handler that refreshes the archive
    const refresh = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // send the mutation to the server
        refreshArchive({ uri })
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: refresh,
    }
    // render
    return (
        <Badge size={20} state="enabled" behaviors={behaviors} style={paintRefresh}
            aria-label="refresh this archive">
            <Icon />
        </Badge>
    )
}


// end of file
