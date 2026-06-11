// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// adjust the look-at center
export const useLookAt = viewport => {
    // adjusting the look-at center mutates the server side store
    const [commit] = useMutation(useLookAtMutation)

    // a scroll fires far faster than the server round trip, so we keep at most one mutation in
    // flight and, while one is, remember only the LATEST center; when the in-flight one settles we
    // send that latest value. this coalesces the storm yet guarantees the final center is not dropped
    const inflight = React.useRef(false)
    const queued = React.useRef(null)

    // send one center to the server
    const send = ({ row, col }) => {
        // mark the channel busy
        inflight.current = true
        // flush whatever was queued once this commit settles either way
        const settle = () => {
            // free again
            inflight.current = false
            // send the most recent center that arrived while we were busy
            const next = queued.current
            if (next) {
                queued.current = null
                send(next)
            }
        }
        // send the request to the server
        commit({
            // input
            variables: {
                input: { viewport, row, col },
            },
            // on success, flush the latest queued center
            onCompleted: settle,
            // on failure, report and still flush, so a transient error does not strand the center
            onError: errors => {
                // show me
                console.log(`viz.viewer.useLookAt:`)
                console.group()
                console.log(`ERROR while setting the look-at center for viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // still flush the latest
                settle()
            },
        })
    }

    // the public handler: send now if idle, otherwise hold only the latest center
    const set = center => {
        // if a commit is in flight
        if (inflight.current) {
            // remember only the most recent center
            queued.current = center
            // and let the in-flight commit flush it
            return
        }
        // otherwise, send it right away
        send(center)
    }

    // return the handler
    return { set }
}


// the mutation that sets the look-at center of a viewport
export const useLookAtMutation = graphql`
    mutation useLookAtMutation($input: ViewLookAtInput!) {
        viewLookAt(input: $input) {
            center {
                dirty
                row
                col
            }
        }
    }
`


// end of file
