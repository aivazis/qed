// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the viewports controller
import { useViewports } from '~/views/viz/viz/useViewports'
// local
// the facade's active-viewport state (a leaf module, so this import adds no cycle)
import { syncActiveViewport, registerActiveSetter } from './activeViewport'


// bridge the ui's active viewport into the {window.qed} facade: push the current value so command
// defaults track what the user selected, and register the setter so {setActive}, split, and collapse
// can move it. it renders nothing and lives inside the viewports provider
export const ViewportBridge = () => {
    // the active viewport and its setter from the viewports context
    const { activeViewport, setActiveViewport } = useViewports()
    // keep the facade's default in sync with the ui
    React.useEffect(() => syncActiveViewport(activeViewport), [activeViewport])
    // and hand the facade the setter so it can move the active viewport in the ui
    React.useEffect(() => registerActiveSetter(setActiveViewport), [setActiveViewport])
    // nothing to draw
    return null
}


// end of file
