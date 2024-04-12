// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// toggle the closed path flag
export const useToggleClosedPath = viewport => {
    // toggling the flag mutates the server side store
    const [commit, pending] = useMutation(useToggleClosedPathMutation)

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
                console.log(`viz.measure.useToggleClosedPath:`)
                console.group()
                console.log(`ERROR while toggling the closed path flag in viewport ${viewport}`)
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


// the mutation that toggles the closed path flag
const useToggleClosedPathMutation = graphql`
    mutation useToggleClosedPathMutation($viewport: Int!) {
        viewMeasureToggleClosedPath(viewport: $viewport) {
            measures {
                dirty
                closed
            }
        }
    }
`


// end of file