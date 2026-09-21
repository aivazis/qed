// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useReachability } from '~/hooks'
// the way back
import { startOver } from '~/automation/startOver'

// locals
import styles from './styles'


// what is left of the app when something in it could not go on
//
// the usual way to get here is a question that was on its way to the server, or was asked,
// while the server was out of reach: it fails, and there is no part of the page that could
// carry on without the answer. that says nothing about the server having shut down, and the
// stream that watches for it is mounted outside the wreckage, so it is still watching. when
// it reports that contact is back, the page starts over, and the user is where they were
//
// the other way to get here is a defect in the client, with the server in plain sight. there
// is no contact to wait for, and starting over by itself could go around in circles, so the
// page says so and leaves the next move to the user
export const Lost = ({ base }) => {
    // find out whether we are in touch with the server
    const { state, since } = useReachability()
    // remember where things stood when we came up
    const arrived = React.useRef(since)
    // watch for contact
    React.useEffect(() => {
        // while we are out of touch, or have not heard either way
        if (state !== "good") {
            // there is nothing to do but wait
            return
        }
        // if we are in touch and nothing has changed since we came up, contact was never the
        // problem, so getting it back is not the cure
        if (since === arrived.current) {
            // leave it to the user
            return
        }
        // otherwise, contact was lost and is back: go again
        startOver()
        // all done
        return
    }, [state, since])

    // while out of touch
    if (state === "error") {
        // say what is going on, and what will happen next
        return (
            <section style={styles.stop} data-qed-lost="waiting">
                <div style={styles.placeholder}>
                    <a href={base} style={styles.link}>qed</a>
                    {" "}
                    has lost contact with its server; this page will come back when the server does
                </div>
            </section>
        )
    }

    // otherwise, the trouble is on this side
    return (
        <section style={styles.stop} data-qed-lost="broken">
            <div style={styles.placeholder}>
                <a href={base} style={styles.link}>qed</a>
                {" "}
                ran into a problem it could not recover from; follow the link to start over
            </div>
        </section>
    )
}


// end of file
