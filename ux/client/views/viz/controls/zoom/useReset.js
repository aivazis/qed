// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// reset the zoom panel to its default state
export const useReset = viewport => {
    // resetting the zoom state modifies the server side store
    const [commit, pending] = useMutation(useResetZoomMutation)

    // make the handler
    const reset = () => {
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
            },
            onError: errors => {
                // show me
                console.log(`viz.zoom.useReset:`)
                console.group()
                console.log(`viewport ${viewport}`)
                console.log(`ERROR while resetting the zoom panel state`)
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
    return { reset }
}


// the mutation that adds an anchor to the path
const useResetZoomMutation = graphql`
    mutation useResetZoomMutation($viewport: Int!) {
        viewZoomReset(viewport: $viewport) {
            zoom {
                dirty
                coupled
                horizontal
                vertical
            }
        }
    }
`


// end of file