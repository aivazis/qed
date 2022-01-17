// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useVisualize } from '../viz/useVisualize'
// context
import { Context } from './context'


// toggle the {coordinate} as the value for {axis}
export const useToggleCoordinate = (axis, coordinate) => {
    // grab my reader and the selector mutator
    const { reader, setSelector, setDataset, setChannel } = React.useContext(Context)
    // and the mutator of the current view
    const visualize = useVisualize()

    // make the toggle
    const toggle = () => {
        // initialize the choice of dataset
        let dataset = null
        // adjust the selector
        setSelector(old => {
            // make a copy of the selector
            const selector = new Map(old)
            // get the current value of the axis
            const current = old.get(axis)
            // if {coordinate} is the current value of {axis}
            if (current === coordinate) {
                // clear it
                selector.delete(axis)
            }
            // otherwise
            else {
                // set it
                selector.set(axis, coordinate)
                // is this new selector enough to resolve the dataset? it has a fighting chance
                // if it has as many values as the reader specifies
                if (selector.size === reader.selectors.length) {
                    // in which case, filter the datasets
                    const candidates = reader.datasets.filter(dataset => {
                        // based on whether their selector
                        for (const { name, value } of dataset.selector) {
                            // fails to match the value in mine
                            if (selector.get(name) !== value) {
                                // reject
                                return false
                            }
                        }
                        // if we get this far, we have a match
                        return true
                    })
                    // there had better be a candidate
                    if (candidates.length === 0) {
                        // if not, complain
                        console.error('FIREWALL: no dataset matches', selector)
                    }
                    // but also no more than one
                    else if (candidates.length > 1) {
                        // if not, complain
                        console.error('FIREWALL: too many dataset matches', selector, candidates)
                        // and pick the first
                        dataset = candidates[0]
                    }
                    // and if there is only one match
                    else {
                        // we got it
                        dataset = candidates[0]
                    }
                }
            }
            // and return the updated selector
            return selector
        })

        // adjust the selected dataset
        setDataset(dataset)
        // any interaction with the dataset selectors clears the channel
        setChannel(null)
        // and update the active view
        visualize({ reader, dataset, channel: null })
        // all done
        return
    }

    // and return it
    return toggle
}


// end of file
