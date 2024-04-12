// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// displace an anchor by a delta
export const useAnchorMove = viewport => {
    // moving an anchor mutates the server side store
    const [commit, pending] = useMutation(useAnchorMoveMutation)

    // make the handler
    const move = ({ handle, delta }) => {
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
                // the node being dragged
                handle,
                // the displacement
                dx: Math.round(delta.x),
                dy: Math.round(delta.y),
            },
            onError: errors => {
                // show me
                console.log(`viz.measure.useAnchorMove:`)
                console.group()
                console.log(`ERROR while moving anchors in viewport ${viewport}`)
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
    return { move }
}


// the mutation that displaces an anchor
const useAnchorMoveMutation = graphql`
    mutation useAnchorMoveMutation($viewport: Int!, $handle:  Int!, $dx: Int!, $dy: Int!) {
        viewMeasureAnchorMove(viewport: $viewport, handle: $handle, dx: $dx, dy: $dy) {
            measures {
                dirty
                path {
                    x
                    y
                }
            }
        }
    }
`


// end of file