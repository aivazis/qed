// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// toggle the anchor selection in single node mode
export const useAnchorToggleSelection = viewport => {
    // toggling the anchor selection mutates the server side store
    const [commit, pending] = useMutation(useAnchorToggleSelectionMutation)

    // make the handler
    const toggle = index => {
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
                console.log(`viz.measure.useAnchorToggleSelection:`)
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
    return { toggle }
}


// the mutation that toggles the anchor selection in single node mode
const useAnchorToggleSelectionMutation = graphql`
    mutation useAnchorToggleSelectionMutation($viewport: Int!, $index: Int!) {
        viewMeasureAnchorToggleSelection(viewport: $viewport, index: $index) {
            measures {
                id
                selection
            }
        }
    }
`


// end of file