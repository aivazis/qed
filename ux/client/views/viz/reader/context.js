// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql } from 'relay-runtime'
import { useFragment } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from '../../main'
import { useQED } from '../../main'

// the provider factory
export const Provider = props => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get the session manager
    const qed = useQED()
    // extract the view information
    const { views } = useFragment(contextGetViewsFragment, qed)
    // get the active view
    const view = views[activeViewport]

    // extract the description of this reader
    const reader = useFragment(contextGetReaderFragment, props.reader)
    // am i the reader in the active viewport?
    const active = view?.reader?.id == reader.id
    // if i'm the active reader, the dataset in the view is mine
    const dataset = active ? view.dataset : (
        // i also know my dataset if there is only possible choice
        reader.datasets.length == 1 ? reader.datasets[0] : null
    )
    // if i'm the active reader, the channel in the view is mine
    const channel = active ? view.channel : (
        // i also know my channel if i have a dataset and it only has one channel
        dataset?.channels.length == 1 ? dataset.channels[0].tag : null
    )


    // MGA: FIXME
    // the selector
    const selector = new Map()

    // let's figure out the set of values for each selector among the available datasets
    const candidates = new Map(reader.selectors.map(selector => [selector.name, new Set()]))

    /*

    // let's figure out the set of values for each selector among the available datasets
    const candidates = new Map(reader.selectors.map(selector => [selector.name, new Set()]))
    // go through the datasets
    reader.datasets.forEach(dataset => {
        dataset.selector.forEach(({ name, value }) => {
            candidates.get(name).add(value)
        })
    })

    // if there is a dataset choice
    if (dataset.current) {
        // use it to initialize my selector
        selector.current = new Map(
            // by going through its coordinate settings and flattening them into key/value pairs
            dataset.current.selector.map(({ name, value }) => [name, value])
        )
        // if it only has one channel
        if (dataset.current.channels.length == 1) {
            // make it the current one
            channel.current = dataset.current.channels[0]
        }
    }
    // otherwise
    else {
        // now, go through the histogram
        candidates.forEach((values, name) => {
            // if we have a selector key that only shows up with one specific value
            if (values.size == 1) {
                // select it
                selector.current.set(name, [...values][0])
            }
        })
    }
    */

    // assemble the context value
    const context = {
        // my details, as harvested from the server
        reader,
        // my state
        active,
        // the dataset
        dataset,
        // the selector
        selector,
        // the channel
        channel,
        // the table of possible choices
        candidates,
    }

    // provide for my children
    return (
        <Context.Provider value={context} >
            {props.children}
        </Context.Provider>
    )
}


// setup the reader context
export const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // my details, as harvested from the server
        reader: null,
        // my state
        active: null,
        // the selected dataset
        dataset: null,
        // the selector
        selector: null,
        // the channel
        channel: null,
        // the possible solutions
        candidates: null,
    }
)


// the fragments
// the information necessary for selecting which datasets to visualize
export const contextGetViewsFragment = graphql`
    fragment contextGetViewsFragment on QED {
        views {
            id
            name
            reader {
                id
                name
                uri
            }
            dataset {
                id
                name
                selector {
                    name
                    value
                }
                channels {
                    id
                    tag
                }
            }
            channel {
                id
                tag
            }
        }
    }
`

// the information necessary of manipulating the set of viewable panels
// must get at least as much as it takes to feed the dataset selection
export const contextGetViewFragment = graphql`
    fragment contextGetViewFragment on View {
        id
        name
        reader {
            id
            name
            uri
        }
        dataset {
            id
            name
            selector {
                name
                value
            }
            channels {
                id
                tag
            }
        }
        channel {
            id
            tag
        }
    }
`

// the information necessary for populating individual entries in the reader sections
// of the dataset panel; {datasets} get the full array; here we extract individual entries
export const contextGetReaderFragment = graphql`
    fragment contextGetReaderFragment on Reader {
        id
        name
        uri
        selectors {
            name
            values
        }
        datasets {
            id
            name
            selector {
                name
                value
            }
            channels {
                id
                tag
            }
        }
    }
`

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
