// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the selection to a single node
export const useSetPixelPathSelection = (viewport) => {
    // get the selection mutator
    const { activeViewport, setPixelPathSelection } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport

    // make a handler that manages the current selection in single node mode
    const select = idx => {
        // reset the selection to contain just my node
        setPixelPathSelection(old => {
            // make a copy of the table
            const table = [...old]
            // reset my entry
            table[viewport] = new Set([idx])
            // and return the updated table
            return table
        })
        // all done
        return
    }

    // make a handler that toggles my node in single node mode
    const toggle = idx => {
        // reset the selection
        setPixelPathSelection(old => {
            // make a copy of the old table
            const table = [...old]
            // get my old entry
            const entry = table[viewport]
            // toggle the selection in single node mode
            table[viewport] = new Set(entry.has(idx) && entry.size === 1 ? [] : [idx])
            // and return the updated table
            return table
        })
        // all done
        return
    }

    // make a handler that toggles my node in multinode mode
    const toggleMultinode = idx => {
        // reset the selection
        setPixelPathSelection(old => {
            // make a copy of the old table
            const table = [...old]
            // make a copy of my old entry
            const clone = new Set([...table[viewport]])
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
            // attach the new entry
            table[viewport] = clone
            // return the updated table
            return table
        })
        // all done
        return
    }

    // make a handler that selects a contiguous list
    const selectContiguous = idx => {
        // reset the selection
        setPixelPathSelection(old => {
            // make a copy of the old table
            const table = [...old]
            // make a copy of my old entry
            const copy = [...table[viewport]]
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
            // make a selection out of it
            table[viewport] = new Set(selection)
            // and return the updated table
            return table
        })
        // all done
        return
    }

    // make a handler that deselects a node unconditionally
    const deselect = idx => {
        // reset the selection to contain just my node
        setPixelPathSelection(old => {
            // find my entry
            const mine = old[viewport]
            // if my target node is not present in the selection
            if (!mine.has(idx)) {
                // we are done; return the {old} table untouched
                return old
            }

            // otherwise, we have to make an adjustment; make a copy of the old table
            const table = [...old]
            // and a copy of my entry
            const copy = new Set([...mine])
            // remove the target node from the selection
            copy.delete(idx)
            // attach my new entry
            table[viewport] = copy
            // and return the updated table
            return table
        })
        // all done
        return
    }

    // and return the handlers
    return { deselect, select, selectContiguous, toggle, toggleMultinode }
}


// end of file
