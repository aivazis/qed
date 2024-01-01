// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { useViews } from '../viz/useViews'
import { useCollapseView } from '../viz/useCollapseView'
// styles
import { disconnect as paintDisconnect } from './styles'


// control to disconnect a data reader
export const Disconnect = ({ uri }) => {
    // get the current views
    const { views } = useViews()
    // and build the handler that collapses them
    const collapse = useCollapseView()
    // build the mutation request
    const [request, isInFlight] = useMutation(disconnectMutation)
    // build the handler that disconnects a reader
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
                const payload = store.getRootField("disconnectReader")
                // ask for the target reader
                const reader = payload.getLinkedRecord("reader")
                // if we didn't get back a valid reader
                if (reader === null) {
                    // something went wrong at the server; there isn't much more to do
                    return
                }
                // get the session manager
                const qed = store.get("QED")
                // get its connected readers
                const readers = qed.getLinkedRecords("readers")
                // remove our target from the pile
                const filtered = readers.filter(
                    // by filtering out entries that match its id
                    entry => entry.getDataID() !== reader.getDataID()
                )
                // attach the modified pile to the session manager
                qed.setLinkedRecords(filtered, "readers")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // go through the views
                const viewports = views.map((view, viewport) => {
                    // and get the list of viewports that show datasets that belong to this reader
                    return view.reader?.uri == uri ? viewport : null
                }).filter(
                    // filter out the nulls
                    viewport => viewport !== null
                ).sort(
                    // and sort in descending order
                    (a, b) => b - a
                ).map(
                    // now go through them
                    viewport => {
                        // collapse the viewport since it shows a dataset from the defunct reader
                        collapse(viewport)
                        // and return the viewport number
                        return viewport
                    }
                )
                // all done
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
    mutation disconnectReaderMutation($uri: String!) {
        disconnectReader(uri: $uri) {
            reader {
                id
            }
        }
    }
`


// end of file