// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// delete an existing anchor
export const useAnchorRemove = viewport => {
    // removing an anchor mutates the server side store
    const [commit, pending] = useMutation(useAnchorRemoveMutation)

    // make the handler
    const remove = ({ anchor }) => {
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
                // the node being removed
                anchor,
            },
            onError: errors => {
                // show me
                console.log(`viz.measure.useAnchorRemove:`)
                console.group()
                console.log(`ERROR while removing anchor ${anchor} in viewport ${viewport}`)
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
    return { remove }
}


// the mutation that adds an anchor to the path
const useAnchorRemoveMutation = graphql`
    mutation useAnchorRemoveMutation($viewport: Int!, $anchor:  Int!) {
        viewMeasureAnchorRemove(viewport: $viewport, anchor: $anchor) {
            measure {
                id
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