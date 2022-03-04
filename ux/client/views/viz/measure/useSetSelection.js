// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the selection to a single node
export const useSetSelection = (idx) => {
    // get the selection mutator
    const { setSelection } = React.useContext(Context)

    // make a handler that manages the current selection in single node mode
    const select = () => {
        // reset the selection to contain my node
        setSelection(new Set([idx]))
        // all done
        return
    }

    // make a handler that toggles my node in multinode mode
    const toggle = () => {
        // reset the selection
        setSelection(old => {
            // make a copy of the old state
            const clone = new Set([...old])
            // if my node is present in the selection
            if (clone.has(idx)) {
                // remove it
                clone.delete(idx)
            }
            // otherwise
            else {
                // add it
                clone.add(idx)
            }
            // return the new selection
            return clone
        })
        // all done
        return
    }

    // make a handler that selects a contiguous list
    const selectContiguous = () => {
        // reset the selection
        setSelection(old => {
            // make a copy of the old selection
            const copy = [...old]
            // sort it
            copy.sort((a, b) => a - b)
            // compute the selection start
            const start = copy.length > 0 ? copy[0] : 0
            // this node could be downstream from mine, so adjust the anchor point to make sure
            // we don't compute invalid selection lengths
            const anchor = (idx < start) ? 0 : start
            // form an array big enough to hold all indices in the range [anchor...idx]
            // and fill it with consecutive integers
            const selection = Array(idx - anchor + 1).fill(0).map((_, i) => anchor + i)
            // make a selection out of it and return it
            return new Set(selection)
        })
        // all done
        return
    }

    // and return the handlers
    return { select, toggle, selectContiguous }
}


// end of file
