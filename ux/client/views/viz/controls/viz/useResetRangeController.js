// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// reset the state of a range controller to its defaults
export const useResetRangeController = ({ viewport, channel }) => {
    // resetting the controller state mutates the server side store
    const [commit, pending] = useMutation(useResetRangeControllerMutation)

    // make the handler
    const reset = ({ controller, setRange, setExtent }) => {
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
                { resetRangeController: { controller: { min, low, high, max } } }
            ) => {
                // reset the range
                setRange({ low, high })
                // and the extent
                setExtent({ min, max })
                // all done
                return
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
        view {
            session
        }
        controller {
            id
            dirty
            min
            low
            high
            max
        }

    }
}`

// end of file
