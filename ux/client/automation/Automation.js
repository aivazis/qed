// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
import { makeQED } from './qed'


// publish {window.qed}, the scriptable automation surface, for the lifetime of the app; it renders
// nothing. mounting it (rather than publishing at import) ties the surface to the app lifecycle and
// leaves room to gate it behind a flag later
export const Automation = () => {
    // publish on mount, withdraw on unmount
    React.useEffect(() => {
        // install the facade
        window.qed = makeQED()
        // and tear it down when the app goes away
        return () => { delete window.qed }
    }, [])

    // nothing to draw
    return null
}


// end of file
