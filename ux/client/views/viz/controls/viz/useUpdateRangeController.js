// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'


// send the updated state of a range controller to the server side store
export const useUpdateRangeController = ({ viewport, channel }) => {
    // updating the controller state mutates the server side store
    const [commit, pending] = useMutation(useUpdateRangeControllerMutation)

    // leave this here, for now
    // make some room for the performance stats
    const [served, setServed] = React.useState(0)
    const [dropped, setDropped] = React.useState(0)
    // make a handler that updates the performance stats
    const monitor = flag => {
        // pick an updater
        const update = flag ? setDropped : setServed
        // and invoke it
        update(old => old + 1)
        // show me
        // console.log(`viz.useUpdateRangeController: served: ${served}, dropped: ${dropped}`)
        // all done
        return
    }

    // make the state update handler
    const update = ({ controller, range, extent }) => {
        // update the statistics
        monitor(pending)
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
                range: {
                    // the viewport
                    viewport,
                    // the channel
                    channel,
                    // the controller
                    controller,
                    // the parameters
                    ...range,
                    ...extent,
                }
            },
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useUpdateRangeController:`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while updating the state of ${controller}`)
                console.log(`for channel ${channel}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }

    // all done
    return { update }
}


// the mutation that updates the controller state
const useUpdateRangeControllerMutation = graphql`
mutation useUpdateRangeControllerMutation($range: RangeControllerUpdateInput!) {
    updateRangeController(range: $range) {
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
