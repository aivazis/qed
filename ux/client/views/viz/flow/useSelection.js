// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// the state of the viewports, which carries the selection
import { Context } from '../viz/context'


// access to the nodes picked on the pipeline diagram
export const useSelection = () => {
    // pull the selection and its mutator from the viewport state
    const { selection, setSelection } = React.useContext(Context)
    // pick a node: on its own, or, when {extend}ing, toggle it in or out of the selection
    const select = (id, extend = false) => {
        // update the selection
        setSelection(old => {
            // a plain pick replaces the selection
            if (!extend) {
                // with just this node
                return [id]
            }
            // otherwise, a node already picked
            if (old.includes(id)) {
                // gets dropped
                return old.filter(other => other !== id)
            }
            // and any other joins the rest
            return [...old, id]
        })
        // all done
        return
    }
    // drop the selection
    const clear = () => {
        // by emptying it
        setSelection([])
        // all done
        return
    }
    // publish
    return { selection, select, clear }
}


// end of file
