// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'
// hooks
import { useVisualize } from '../viz/useVisualize'


// make a handler that updates the view with the current reader context
export const useUpdateView = () => {
    // grab the relevant refs from my context
    const { reader, dataset, selector, channel } = React.useContext(Context)
    // and the current view mutator
    const visualize = useVisualize()

    // make the handler
    const update = () => {
        // get the current selector
        const currentSelector = selector.current

        // if my selector is fully resolved
        if (currentSelector.size === reader.selectors.length) {
            // look for the matching dataset by filtering out the ones
            const candidates = reader.datasets.filter(dataset => {
                // whose selectors
                for (const { name, value } of dataset.selector) {
                    // fail to match any of my values for their axes
                    if (currentSelector.get(name) != value) {
                        // in which case they get rejected
                        return false
                    }
                }
                // if we got this far, we have a match
                return true
            })
            // if there is a candidate
            if (candidates) {
                // select it
                dataset.current = candidates[0]
                // if the current value of the channel is not among the valid choices
                if (!dataset.current.channels.includes(channel.current)) {
                    // reset the channel
                    channel.current = null
                }
                // if there were actually more than one match
                if (candidates.length > 1) {
                    // complain
                    console.error('FIREWALL: too many datasets match', currentSelector, candidates)
                }
            }
            // otherwise, something is wrong
            else {
                // reset the dataset
                dataset.current = null
                // and the channel
                channel.current = null
                // complain
                console.error('FIREWALL: no datasets match', currentSelector)
            }
        }
        // if not
        else {
            // reset the dataset
            dataset.current = null
            // and the channel
            channel.current = null
        }

        // update the view
        visualize({ reader, dataset: dataset.current, channel: channel.current })

        // all done
        return
    }

    // and return it
    return update
}


// end of file
