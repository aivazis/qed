// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// update the sync state of some aspect a viewport
export const useSyncUpdateOffset = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(useSyncUpdateOffsetMutation)
    // make a handler that updates the layer state
    const update = ({ viewport, offset }) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                input: {
                    // the payload
                    viewport,
                    x: offset.x,
                    y: offset.y,
                }
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useSyncUpdateOffset: viewport ${viewport}`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while updating the offsets in the sync table`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }
    // and return it
    return { update }
}

// the mutation that updates the scroll sync state
const useSyncUpdateOffsetMutation = graphql`
    mutation useSyncUpdateOffsetMutation($input: ViewSyncUpdateOffsetInput!) {
        viewSyncUpdateOffset(input: $input) {
            sync {
                offsets {x y}
            }
        }
    }
`


// end of file
