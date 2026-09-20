// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'


// ask the server to bring back the trees of the archives
// the server keeps the record of which folders were on display, e.g. from an earlier session,
// but it does not list any of them until a client says the archives are relevant; showing the
// archives panel is that declaration. a folder that is on display, has no listing under way,
// has not failed, and shows nothing is the sign of a tree that has not come back yet. a folder
// that is honestly empty looks the same, which costs one request that changes nothing
export const useRestoreArchives = archives => {
    // build the mutation request
    const [request, isInFlight] = useMutation(useRestoreArchivesMutation)
    // collect the folders that are on display with nothing to show
    const waiting = []
    // go through the archives
    for (const archive of archives) {
        // the locations that have something beneath them on display
        const populated = new Set(archive.items.map(item => item.parent))
        // the root of the archive
        if (archive.expanded && !archive.pending && !archive.error && !populated.has(archive.uri)) {
            // is waiting
            waiting.push(archive.uri)
        }
        // and so is every folder within it
        for (const item of archive.items) {
            // that is in the same state
            if (item.isFolder && item.expanded && !item.pending && !item.error
                && !populated.has(item.uri)) {
                // so add it to the pile
                waiting.push(item.uri)
            }
        }
    }
    // form the signature of the pile, so the effect fires only when its composition changes
    const signature = waiting.join(",")
    // the signature of the last request, so that folders the server cannot fill, e.g. the
    // ones that are honestly empty, are asked about once rather than in a loop
    const attempted = React.useRef(null)
    // schedule the request
    React.useEffect(() => {
        // when the pile drains, forget the last attempt, so a tree that regresses, e.g. after
        // a server restart, gets asked about again
        if (waiting.length === 0) {
            // clear the mark
            attempted.current = null
            // and there is nothing to ask for
            return
        }
        // if a request is already on its way, or this pile has already been asked about
        if (isInFlight || attempted.current === signature) {
            // there is nothing to do
            return
        }
        // leave the mark
        attempted.current = signature
        // and ask the server to bring the trees back; the payload carries them, and relay
        // merges them into the archive records, so no updater is necessary
        request({
            // the request concerns every archive, so the payload names none
            variables: { input: {} },
        })
        // all done
        return
    }, [signature, isInFlight])
    // all done
    return
}


// the mutation, exported so the automation facade can commit the same document
export const useRestoreArchivesMutation = graphql`
    mutation useRestoreArchivesMutation($input: RestoreArchivesInput!) {
        restoreArchives(input: $input) {
            archives {
                id
                expanded
                pending
                error
                hits
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`


// end of file
