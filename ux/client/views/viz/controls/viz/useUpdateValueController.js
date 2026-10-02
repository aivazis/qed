// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// locals
import { quiet } from '../../traffic'


// send the updated state of a value controller to the server side store
export const useUpdateValueController = ({ viewport, channel }) => {
    // updating the controller state mutates the server side store
    const [commit] = useMutation(useUpdateValueControllerMutation)

    // a drag fires updates far faster than the server can render them, so we keep at most one
    // update in flight and, while it is, remember only the LATEST one; when the in-flight one has
    // settled and the viewport shows its tiles, or a second has passed, we send that latest value.
    // this paces the updates by the screen, so the server renders only screens that get seen, yet
    // guarantees the final resting value is never dropped, wherever the drag ends
    const inflight = React.useRef(false)
    const queued = React.useRef(null)

    // send one update to the server
    const send = args => {
        // unpack
        const { controller, value, extent } = args
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
                input: { viewport, channel, controller, value, ...extent },
            },
            // on success, flush the latest queued update once the viewport shows the tiles of
            // this one, but wait no longer than a second: a change invalidates every tile on the
            // screen, and a change sent before they arrive asks for a screen nobody will see
            onCompleted: () => quiet(viewport).then(settle),
            // on failure, report and still flush, so a transient error does not strand the value
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useUpdateValueController:`)
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
export const useUpdateValueControllerMutation = graphql`
mutation useUpdateValueControllerMutation($input: ViewValueUpdateInput!) {
    viewValueUpdate(input: $input) {
        view {
            session
        }
        controller {
            id
            dirty
            auto
            min
            value
            max
        }
    }
}`


// end of file
