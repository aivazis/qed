// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// adjust the zoom levels
export const useSetLevel = viewport => {
    // adjusting the zoom levels mutates the server side store
    const [commit] = useMutation(useSetLevelZoomMutation)

    // a drag fires far faster than the server round trip, so we keep at most one mutation in flight
    // and, while one is, remember only the LATEST level; when the in-flight one settles we send that
    // latest value. this coalesces the storm yet guarantees the final resting level is never dropped
    const inflight = React.useRef(false)
    const queued = React.useRef(null)

    // send one level to the server
    const send = ({ horizontal, vertical }) => {
        // mark the channel busy
        inflight.current = true
        // flush whatever was queued once this commit settles either way
        const settle = () => {
            // free again
            inflight.current = false
            // send the most recent level that arrived while we were busy
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
                input: { viewport, horizontal, vertical },
            },
            // on success, flush the latest queued level
            onCompleted: settle,
            // on failure, report and still flush, so a transient error does not strand the level
            onError: errors => {
                // show me
                console.log(`viz.zoom.useLevel:`)
                console.group()
                console.log(`ERROR while setting the zoom level for viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // still flush the latest
                settle()
            },
        })
    }

    // the public handler: send now if idle, otherwise hold only the latest level
    const set = level => {
        // if a commit is in flight
        if (inflight.current) {
            // remember only the most recent level
            queued.current = level
            // and let the in-flight commit flush it
            return
        }
        // otherwise, send it right away
        send(level)
    }

    // return the handler
    return { set }
}


// the mutation that adds an anchor to the path
export const useSetLevelZoomMutation = graphql`
    mutation useSetLevelZoomMutation($input: ViewZoomSetLevelInput!) {
        viewZoomSetLevel(input: $input) {
            zooms {
                dirty
                horizontal
                vertical
            }
        }
    }
`


// end of file