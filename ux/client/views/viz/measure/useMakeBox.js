// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// delete an existing anchor
export const useMakeBox = viewport => {
    // converting a pair of anchors into a box mutates the server store
    const [commit, pending] = useMutation(useMakeBoxMutation)

    // make the handler
    const box = () => {
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
                console.log(`viz.measure.useMakeBox:`)
                console.group()
                console.log(`ERROR while attempting to make a box in viewport ${viewport}`)
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
    return { box }
}


// the mutation that deletes an anchor
const useMakeBoxMutation = graphql`
    mutation useMakeBoxMutation($viewport: Int!) {
        viewMeasureMakeBox(viewport: $viewport) {
            measures {
                dirty
                closed
                path {
                    x
                    y
                }
                selection
            }
        }
    }
`


// end of file
