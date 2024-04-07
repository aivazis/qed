// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// adjust the zoom levels
export const useSetLevel = viewport => {
    // adjusting the zoom levels mutates the server side store
    const [commit, pending] = useMutation(useSetLevelZoomMutation)

    // make the handler
    const set = ({ horizontal, vertical }) => {
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
                // the zoom levels
                horizontal,
                vertical,
            },
            onError: errors => {
                // show me
                console.log(`viz.zoom.useLevel:`)
                console.group()
                console.log(`ERROR while setting the zoom level for viewport ${viewport}`)
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
    return { set }
}


// the mutation that adds an anchor to the path
const useSetLevelZoomMutation = graphql`
    mutation useSetLevelZoomMutation($viewport: Int!, $horizontal: Float!, $vertical: Float!) {
        viewZoomSetLevel(viewport: $viewport, horizontal: $horizontal, vertical: $vertical) {
            zoom {
                dirty
                horizontal
                vertical
            }
        }
    }
`


// end of file