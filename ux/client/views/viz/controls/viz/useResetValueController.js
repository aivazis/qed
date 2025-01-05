// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// reset the state of a value controller to its defaults
export const useResetValueController = ({ viewport, channel }) => {
    // resetting the controller state mutates the server side store
    const [commit, pending] = useMutation(useResetValueControllerMutation)

    // make the handler
    const reset = ({ controller, setMarker, setExtent }) => {
        // if there is a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            // input
            variables: {
                // the payload
                controller: {
                    // the viewport
                    viewport,
                    // the channel
                    channel,
                    // the controller
                    controller,
                }
            },
            onCompleted: (
                { resetValueController: { controller: { min, value, max } } }
            ) => {
                // reset the range
                setMarker(value)
                // and the extent
                setExtent({ min, max })
                // all done
                return
            },
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useResetValueController:`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while resetting the state of ${controller}`)
                console.log(`for channel ${channel}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
    }

    // all done
    return { reset }
}


// the mutation that resets the controller state
const useResetValueControllerMutation = graphql`
mutation useResetValueControllerMutation($controller: ValueControllerResetInput!) {
    resetValueController(controller: $controller) {
        view {
            session
        }
        controller {
            id
            dirty
            min
            value
            max
        }

    }
}`

// end of file
