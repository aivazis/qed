// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// the node being dragged on the pipeline diagram: where it is headed, and where the server has it
// now, both in diagram coordinates; the connectors and labels attached to it read it, so they
// follow the node while it moves. the shift is the difference of the two, so a server that moves
// the node mid-drag, as it does for a live viewport, never makes it travel twice
const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // nothing is being dragged
        drag: null,
        setDrag: () => { throw new Error('no drag provider') },
    }
)


// the provider
export const DragProvider = ({ children }) => {
    // the drag in progress, as { id, tx, ty, ax, ay }, or nothing
    const [drag, setDrag] = React.useState(null)
    // provide for my children
    return (
        <Context.Provider value={{ drag, setDrag }}>
            {children}
        </Context.Provider>
    )
}


// access to the drag in progress
export const useDrag = () => {
    // pull it from the context
    const { drag, setDrag } = React.useContext(Context)
    // how far the node with {id} is from where it is headed, which is nowhere unless it is the
    // one being dragged
    const shiftOf = id => (drag !== null && drag.id === id)
        ? { dx: drag.tx - drag.ax, dy: drag.ty - drag.ay }
        : { dx: 0, dy: 0 }
    // publish
    return { drag, setDrag, shiftOf }
}

// end of file
