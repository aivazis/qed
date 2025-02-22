// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// styles
import { disconnect as paintDisconnect } from './styles'


// control to disconnect a data archive
export const Disconnect = ({ uri }) => {
    // build the mutation request
    const [request, isInFlight] = useMutation(disconnectMutation)
    // build the handler that disconnects an archive
    const disconnect = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // if there is already a pending operation
        if (isInFlight) {
            // skip the update
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                uri
            },
            // update the store
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("disconnectArchive")
                // ask for the target archive
                const archive = payload.getLinkedRecord("archive")
                // if we didn't get back a valid archive
                if (archive === null) {
                    // something went wrong at the server; there isn't much more to do
                    return
                }
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const archives = qed.getLinkedRecords("archives")
                // remove our target from the pile
                const filtered = archives.filter(
                    // by filtering out entries that match its id
                    entry => entry.getDataID() !== archive.getDataID()
                )
                // attach the modified pile to the session manager
                qed.setLinkedRecords(filtered, "archives")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // not much to do, for now
                return
            }
        })
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: disconnect,
    }
    // render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={paintDisconnect}>
            <Icon />
        </Badge>

    )
}


// the mutation that disconnects an archive
const disconnectMutation = graphql`
    mutation disconnectArchiveMutation($uri: String!) {
        disconnectArchive(uri: $uri) {
            archive {
                id
            }
        }
    }
`


// end of file