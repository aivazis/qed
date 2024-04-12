// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// add a new anchor to the path
export const useAnchorAdd = viewport => {
    // adding an anchor to the path mutates the server side store
    const [commit, pending] = useMutation(useAnchorAddMutation)

    // make the handler
    const add = (anchor, index = null) => {
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
                // the anchor coordinates
                ...anchor,
                // the index
                index,
            },
            onError: errors => {
                // show me
                console.log(`viz.measure.useAnchorAdd:`)
                console.group()
                console.log(`ERROR while adding an anchor to viewport ${viewport}`)
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
    return { add }
}


// the mutation that adds an anchor to the path
const useAnchorAddMutation = graphql`
    mutation useAnchorAddMutation($viewport: Int!, $x: Int!, $y: Int!, $index: Int) {
        viewMeasureAnchorAdd(viewport: $viewport, x: $x, y: $y, index: $index) {
            measures {
                id
                path {
                    x
                    y
                }
            }
        }
    }
`


// end of file