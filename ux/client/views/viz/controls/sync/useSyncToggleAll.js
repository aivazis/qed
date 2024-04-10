// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the state of a sync aspect for all viewports
export const useSyncToggleAll = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(useSyncToggleAllMutation)
    // make a handler that toggles all flags of a given aspect
    const toggle = ({ viewport, aspect }) => {
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
                aspect
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useToggleAllSync:`)
                console.group()
                console.log(`viewport ${viewport}:`)
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
const useSyncToggleAllMutation = graphql`
    mutation useSyncToggleAllMutation($viewport: Int!, $aspect: String!) {
        viewSyncToggleAll(viewport: $viewport, aspect: $aspect) {
            sync {
                dirty
                channel
                zoom
                scroll
                path
            }
        }
    }
`


// end of file
