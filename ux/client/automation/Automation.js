// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
import { makeQED } from './qed'


// the surface is opt-in, so default production never exposes it: enable it with the {?automation} url
// param (handy in dev and the devtools console) or the {qed.automation} localStorage flag (which the
// test harness sets)
const enabled = () => {
    try {
        return new URLSearchParams(window.location.search).has("automation")
            || window.localStorage.getItem("qed.automation") === "1"
    } catch {
        // a locked-down context with no {localStorage}; treat as not enabled
        return false
    }
}


// publish {window.qed}, the scriptable automation surface, for the lifetime of the app, when opted
// in; it renders nothing. mounting it (rather than publishing at import) ties the surface to the app
// lifecycle and lets the gate consult the live url and storage
export const Automation = () => {
    // publish on mount, withdraw on unmount
    React.useEffect(() => {
        // unless opted in, stay invisible
        if (!enabled()) {
            return undefined
        }
        // install the facade
        window.qed = makeQED()
        // and tear it down when the app goes away
        return () => { delete window.qed }
    }, [])

    // nothing to draw
    return null
}


// end of file
