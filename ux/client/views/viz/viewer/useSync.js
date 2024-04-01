// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the state of the measure layer for a viewport
export const useToggleScroll = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(toggleScrollSyncMutation)
    // make a handler that toggles the layer state
    const toggle = (viewport, reader) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                viewport,
                reader: reader,
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useToggleScrollSync:`)
                console.group()
                console.log(`ERROR while toggling the scroll sync status in viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }
    // and return it
    return { toggle }
}


// toggle the state of a sync aspect for all viewports
export const useToggleAll = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(toggleAllSyncMutation)
    // make a handler that toggles all flags of a given aspect
    const toggle = (viewport, reader, aspect) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                viewport,
                reader: reader,
                aspect
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useToggleAllSync:`)
                console.group()
                console.log(`ERROR while toggling the '${aspect}' sync status of all viewports`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })

        // all done
        return
    }
    // and return it
    return { toggle }
}

// the mutation that toggles the scroll sync state
const toggleScrollSyncMutation = graphql`
    mutation useSyncToggleScrollSyncMutation($viewport: Int!, $reader: String!) {
        viewToggleScrollSync(viewport: $viewport, reader: $reader) {
            sync {
                scroll
            }
        }
    }
`

// the mutation that toggles the scroll sync state
const toggleAllSyncMutation = graphql`
    mutation useSyncToggleAllSyncMutation($viewport: Int!, $reader: String!, $aspect: String!) {
        viewToggleAllSync(viewport: $viewport, reader: $reader, aspect: $aspect) {
            sync {
                channel
                zoom
                scroll
                path
            }
        }
    }
`


// end of file
