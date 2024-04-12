// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// toggle the sync state of some aspect a viewport
export const useSyncToggleViewport = () => {
    // toggling the measure layer state mutates the server side store
    const [request, pending] = useMutation(useSyncToggleViewportMutation)
    // make a handler that toggles the layer state
    const toggle = ({ viewport, aspect }) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                viewport,
                aspect
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.measure.useSyncToggleViewport: viewport ${viewport}`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while toggling the ${aspect} sync`)
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
    return { toggle }
}

// the mutation that toggles the scroll sync state
const useSyncToggleViewportMutation = graphql`
    mutation useSyncToggleViewportMutation($viewport: Int!, $aspect: String!) {
        viewSyncToggleViewport(viewport: $viewport, aspect: $aspect) {
            view {
                channel {
                    tag
                }
                measure {
                    dirty
                    active
                    path {x y}
                    closed
                    selection
                }
                sync {
                    dirty
                    channel
                    zoom
                    scroll
                    path
                }
                zoom {
                    dirty
                    coupled
                    horizontal
                    vertical
                }
            }
        }
    }
`


// end of file
