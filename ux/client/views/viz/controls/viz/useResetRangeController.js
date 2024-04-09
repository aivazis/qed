// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// reset the state of a range controller to its defaults
export const useResetRangeController = ({ viewport, channel }) => {
    // resetting the controller state mutates the server side store
    const [commit, pending] = useMutation(useResetRangeControllerMutation)

    // make the handler
    const reset = ({ controller }) => {
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
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useResetRangeController:`)
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
const useResetRangeControllerMutation = graphql`
mutation useResetRangeControllerMutation($controller: RangeControllerResetInput!) {
    resetRangeController(controller: $controller) {
        controller {
            id
        }

    }
}`

// end of file
