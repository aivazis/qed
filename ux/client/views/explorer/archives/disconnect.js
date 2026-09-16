// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// the store updater the archive mutations share
import { disconnectArchiveUpdater } from './archiveListUpdaters'
// styles
import { disconnect as paintDisconnect } from './styles'


// control to disconnect a data archive
export const Disconnect = ({ uri }) => {
    // build the mutation request
    const [request, isInFlight] = useMutation(disconnectArchiveMutation)
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
                input: {
                    // the payload
                    uri
                }
            },
            // update the store
            updater: disconnectArchiveUpdater,
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
        <Badge size={10} state="enabled" behaviors={behaviors} style={paintDisconnect}
            aria-label="disconnect this archive">
            <Icon />
        </Badge>

    )
}


// the mutation that disconnects an archive
export const disconnectArchiveMutation = graphql`
    mutation disconnectArchiveMutation($input: DisconnectArchiveInput!) {
        disconnectArchive(input: $input) {
            archive {
                id
            }
        }
    }
`


// end of file