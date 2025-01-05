// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the state of the measure layer for a viewport
export const useMeasureToggleLayer = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(measureToggleLayerMutation)

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
                console.error(`viz.measure.useMeasureToggleLayer:`)
                console.group()
                console.log(`ERROR while toggling the measure layer in viewport ${viewport}`)
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

// the mutation that toggles the measure layer state
const measureToggleLayerMutation = graphql`
    mutation useMeasureToggleLayerMutation($viewport: Int!, $reader: String!) {
        viewMeasureToggleLayer(viewport: $viewport, reader: $reader) {
            measures{
                dirty
                active
            }
        }
    }
`

// end of file
