// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// adjust the zoom levels
export const useToggleCoupled = viewport => {
    // adjusting the zoom levels mutates the server side store
    const [commit, pending] = useMutation(useToggleCoupledZoomMutation)

    // make the handler
    const toggle = () => {
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
                console.log(`viz.zoom.useToggleCoupled:`)
                console.group()
                console.log(`ERROR while toggling the coupled zoom flag for viewport ${viewport}`)
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


// the mutation that adds an anchor to the path
const useToggleCoupledZoomMutation = graphql`
    mutation useToggleCoupledZoomMutation($viewport: Int!) {
        viewZoomToggleCoupled(viewport: $viewport) {
            zoom {
                dirty
                coupled
            }
        }
    }
`


// end of file