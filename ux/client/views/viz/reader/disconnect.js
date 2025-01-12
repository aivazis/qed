// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import { graphql, useFragment, useMutation } from 'react-relay/hooks'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { useCollapseView } from '../viz/useCollapseView'
// styles
import { disconnect as paintDisconnect } from './styles'


// control to disconnect a data reader
export const Disconnect = ({ qed, name }) => {
    // extract the view information
    const { views } = useFragment(disconnectReaderGetViewsFragment, qed)
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
                name
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
                    return view.reader?.name == name ? viewport : null
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
                // report
                console.group(`viz.reader.disconnect:`)
                console.log(`disconnecting '${name}' collapsed [${viewports}]`)
                console.groupEnd()
                // all done
                return
            },
            onError: errors => {
                // send the error to the console
                console.error(
                    `viz.reader.disconnect: ERROR while disconnecting '${reader.name}'`
                )
                console.group()
                console.log(errors)
                console.groupEnd()
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
    mutation disconnectReaderMutation($name: String!) {
                    disconnectReader(name: $name) {
            reader {
                            id
                        }
                    }
                }
                `

// information about views
const disconnectReaderGetViewsFragment = graphql`
    fragment disconnectReaderViewsFragment on QED {
        views {
            reader {
                            name
                        }
                    }
                }
                `


// end of file