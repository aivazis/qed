// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the state of the flow layer for a viewport
export const useFlowToggleLayer = () => {
    // toggling the flow layer state mutates the server side store
    const [request, pending] = useMutation(flowToggleLayerMutation)

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
                reader
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.flow.useFlowToggleLayer:`)
                console.group()
                console.log(`ERROR while toggling the flow layer in viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })

    }

    // and return it
    return { toggle }
}

// the mutation that toggles the flow layer state
const flowToggleLayerMutation = graphql`
    mutation useFlowToggleLayerMutation($viewport: Int!, $reader: String!) {
        viewFlowToggleLayer(viewport: $viewport, reader: $reader) {
            flow {
                active
            }
        }
    }
`

// end of file
