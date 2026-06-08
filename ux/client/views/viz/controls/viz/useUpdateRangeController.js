// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'


// send the updated state of a range controller to the server side store
export const useUpdateRangeController = ({ viewport, channel }) => {
    // updating the controller state mutates the server side store
    const [commit] = useMutation(useUpdateRangeControllerMutation)

    // a drag fires updates far faster than the server round trip, so we keep at most one mutation
    // in flight and, while it is, remember only the LATEST update; when the in-flight one settles
    // we send that latest value. this coalesces the storm yet guarantees the final resting value is
    // never dropped (the bug fixed here), regardless of where in the round trip the drag ends
    const inflight = React.useRef(false)
    const queued = React.useRef(null)

    // send one update to the server
    const send = args => {
        // unpack
        const { controller, range, extent } = args
        // mark the channel busy
        inflight.current = true
        // flush whatever the in-flight commit left queued, once it settles either way
        const settle = () => {
            // the channel is free again
            inflight.current = false
            // if a later update arrived while we were busy, send the most recent one now
            const next = queued.current
            if (next) {
                // consume it
                queued.current = null
                // and send it
                send(next)
            }
        }
        // commit the mutation
        commit({
            // the payload
            variables: {
                input: { viewport, channel, controller, ...range, ...extent },
            },
            // on success, flush the latest queued update
            onCompleted: settle,
            // on failure, report and still flush, so a transient error does not strand the value
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useUpdateRangeController:`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while updating the state of ${controller}`)
                console.log(`for channel ${channel}`)
                console.log(errors)
                console.groupEnd()
                // still flush the latest
                settle()
            },
        })
    }

    // the public handler: send now if the channel is idle, otherwise hold only the latest update
    // and let the in-flight commit's completion flush it
    const update = args => {
        // if a commit is in flight
        if (inflight.current) {
            // remember only the most recent request
            queued.current = args
            // and wait for the in-flight one to flush it
            return
        }
        // otherwise, send it right away
        send(args)
    }

    // all done
    return { update }
}


// the mutation that updates the controller state
export const useUpdateRangeControllerMutation = graphql`
mutation useUpdateRangeControllerMutation($input: ViewRangeUpdateInput!) {
    viewRangeUpdate(input: $input) {
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
