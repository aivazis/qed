// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// add a new anchor halfway between two existing ones
export const useAnchorSplit = viewport => {
    // adding an anchor mutates the server side store
    const [commit, pending] = useMutation(useAnchorSplitMutation)

    // make the handler
    const split = ({ anchor }) => {
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
                console.log(`viz.measure.useAnchorSplit:`)
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
    return { split }
}


// the mutation that adds an anchor to the path
const useAnchorSplitMutation = graphql`
    mutation useAnchorSplitMutation($viewport: Int!, $anchor:  Int!) {
        viewMeasureAnchorSplit(viewport: $viewport, anchor: $anchor) {
            measures {
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