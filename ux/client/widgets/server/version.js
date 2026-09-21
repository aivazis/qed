// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useServerQuery } from './useSyncWithServer'
// styles
import styles from './styles'


export const Version = ({ qref, style, standing }) => {
    // query the server
    const { version } = useServerQuery(qref)
    // unpack the version info
    const { major, minor, micro, revision } = version
    // unpack where we stand with the server; a caller that does not track it leaves us
    // saying nothing about it, which is what this widget did before there was anything to say
    const { state = "unknown", since = null } = standing ?? {}

    // merge the overall styles
    const base = { ...style.box, ...styles.box, ...style.text, ...styles.text }
    // and the decoration that goes with where we stand
    const status = { ...style.status?.[state], ...styles.status?.[state] }

    // a client that has lost its event stream is out of touch: the browser is retrying on
    // its own, and until it succeeds everything on this page is as old as the last frame
    // that arrived. say so, rather than leaving a stale picture looking live
    if (state === "error") {
        // name when it happened, since how stale the page is is the useful part
        const title = since
            ? `no contact with the server since ${since.toString()}`
            : "no contact with the server"
        // and say it in the value column, not in the color alone
        return (
            <div style={{ ...base, ...status }} title={title} data-qed-server="lost">
                qed server {major}.{minor}.{micro} rev {revision} — no contact
            </div>
        )
    }

    // otherwise we are in touch; get the time
    const now = new Date()
    // use it to make a timestamp
    const title = `last checked on ${now.toString()}`
    // assemble the version
    return (
        <div style={{ ...base, ...status }} title={title} data-qed-server={state}>
            qed server {major}.{minor}.{micro} rev {revision}
        </div>
    )
}


// end of file
