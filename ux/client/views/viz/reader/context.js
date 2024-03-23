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
import { useGetView } from '../../main/useGetView'


// the provider factory
export const Provider = (props) => {
    // extract the data
    const reader = useFragment(graphql`
        fragment context_viz_connected_reader on Reader {
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
        }`,
        props.reader
    )

    // get the active view
    const view = useGetView()

    // set up my state
    // am i the active reader?
    const active = view?.reader?.id == reader.id
    // my selected dataset
    const dataset = React.useRef(null)
    // the selector
    const selector = React.useRef(new Map())
    // and my channel selection
    const channel = React.useRef(null)

    // if i'm the active reader
    if (active) {
        // if the view has a dataset
        if (view.dataset) {
            // it must be mine
            dataset.current = view.dataset
        }
        // if the view has a channel
        if (view.channel) {
            // it's my channel
            channel.current = view.channel
        }
    } else {
        // if i only have one dataset, pick it
        const myDataset = reader.datasets.length == 1 ? reader.datasets[0] : null
        // and use it to initialize my dataset of choice
        dataset.current = myDataset
        // reset my selector
        selector.current = new Map()
        // and my channel
        channel.current = null
    }

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


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
