// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// place an existing anchor at new coordinates
export const useAnchorPlace = viewport => {
    // placing an anchor mutates the server side store
    const [commit, pending] = useMutation(useAnchorPlaceMutation)

    // make the handler
    const place = ({ handle, position }) => {
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
                // the node being placed
                handle,
                // the displacement
                x: Math.round(position.x),
                y: Math.round(position.y),
            },
            onError: errors => {
                // show me
                console.log(`viz.measure.useAnchorPlace:`)
                console.group()
                console.log(`ERROR while placing an anchor in viewport ${viewport}`)
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
    return { place }
}


// the mutation that places an anchor at a specific location
const useAnchorPlaceMutation = graphql`
    mutation useAnchorPlaceMutation($viewport: Int!, $handle:  Int!, $x: Int!, $y: Int!) {
        viewMeasureAnchorPlace(viewport: $viewport, handle: $handle, x: $x, y: $y) {
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