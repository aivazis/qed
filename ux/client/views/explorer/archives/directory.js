// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useArchive } from './useArchive'
import { useDirectoryContentsLoader } from './useFetchDirectoryContents'
// components
import { Contents } from './contents'

// the panel with the directory contents
export const Directory = ({ uri }) => {
    // get the archive
    const archive = useArchive()
    // preload the query
    const [qref, getContents] = useDirectoryContentsLoader()
    // schedule the contents fetch
    React.useEffect(() => {
        // variables
        const variables = { archive: archive.uri, path: uri, }
        // options
        const options = { fetchPolicy: "store-and-network" }
        // fetch
        getContents(variables, options)
        // all done
        return
    }, [])
    // if the data is not available yet
    if (qref === null) {
        // bail
        return
    }
    // otherwise, render the directory contents
    return (
        <Contents qref={qref} />
    )
}


// end of file
