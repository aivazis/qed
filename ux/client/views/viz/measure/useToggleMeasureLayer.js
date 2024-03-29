// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the state of the measure layer for a viewport
export const useToggleMeasureLayer = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(toggleMeasureLayerMutation)

    // make a handler that toggles the layer state
    const toggle = dataset => {
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
                dataset
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useToggleMeasureLayer:`)
                console.group()
                console.log(`ERROR while toggling the '${dataset}' measure layer`)
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
const toggleMeasureLayerMutation = graphql`
    mutation useToggleMeasureLayerMutation($dataset: String!) {
        datasetToggleMeasureLayer(dataset: $dataset) {
            measure{
                active
            }
        }
    }
`

// end of file
