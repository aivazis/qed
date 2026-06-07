// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the {window.qed} facade's notion of the active viewport, in a leaf module so both the facade and
// the {ViewportBridge} that keeps it in sync with the ui can import it without an import cycle

// the viewport facade commands target when the caller names none
let active = 0
// the ui's active-viewport setter, registered by the bridge when it mounts
let uiSetter = null

// read the active viewport
export const getActiveViewport = () => active
// the bridge pushes the ui's active viewport here, so command defaults track what the user selected
export const syncActiveViewport = viewport => { active = viewport }
// the bridge registers the ui's setter, so the facade can move the active viewport too
export const registerActiveSetter = setter => { uiSetter = setter }
// set the active viewport in the facade and -- when the bridge is mounted -- the ui
export const activate = viewport => {
    active = viewport
    uiSetter?.(viewport)
}


// end of file
