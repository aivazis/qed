// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// extend the anchor selection to include a specific index
export const useAnchorExtendSelection = viewport => {
    // extending the anchor selection mutates the server side store
    const [commit, pending] = useMutation(useAnchorExtendSelectionMutation)

    // make the handler
    const select = index => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the request to the server
        commit({
            // input
            variables: {
                // the payload
                // the viewport
                viewport,
                // the anchor index
                index,
            },
            onError: errors => {
                // show me
                console.log(`viz.measure.useAnchorExtendSelection:`)
                console.group()
                console.log(`ERROR while modifying the anchor selection in viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }

    // return the handler
    return { select }
}


// the mutation that adds an anchor to the path
const useAnchorExtendSelectionMutation = graphql`
    mutation useAnchorExtendSelectionMutation($viewport: Int!, $index: Int!) {
        viewMeasureAnchorExtendSelection(viewport: $viewport, index: $index) {
            measures {
                dirty
                selection
            }
        }
    }
`


// end of file