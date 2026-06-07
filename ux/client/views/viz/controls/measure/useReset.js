// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// reset the zoom panel to its default state
export const useReset = viewport => {
    // resetting the measure state modifies the server side store
    const [commit, pending] = useMutation(resetMeasureMutation)

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
                input: {
                    // the payload
                    // the viewport
                    viewport,
                }
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


// the mutation that resets the measure layer; exported so the {window.qed} automation facade can
// commit it against the live store exactly as this hook does
export const resetMeasureMutation = graphql`
    mutation useResetMeasureMutation($input: ViewMeasureResetInput!) {
        viewMeasureReset(input: $input) {
            measures {
                dirty
                active
                closed
                path {x y}
                selection
            }
        }
    }
`


// end of file