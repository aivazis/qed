// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql } from 'relay-runtime'
import { useFragment } from 'react-relay/hooks'

// local
// hooks
import { useGetView } from '../viz/useGetView'


// the provider factory
export const Provider = (props) => {
    // extract the data
    const reader = useFragment(graphql`
        fragment context_reader on Reader {
            id
            uuid
            uri
            api
            selectors {
                name
                values
            }
            datasets {
                uuid
                datatype
                selector {
                    name
                    value
                }
                channels
                shape
                origin
                tile
            }
        }`,
        props.reader
    )

    // set up my state
    // am i the active reader?
    const active = React.useRef(false)
    // my selected dataset
    const dataset = React.useRef(null)
    // the selector
    const selector = React.useRef(new Map())
    // and my channel selection
    const channel = React.useRef(null)

    // get the active view
    const view = useGetView()
    // if i'm the active reader
    if (view?.reader?.uuid === reader.uuid) {
        // mark me as active
        active.current = true
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
        // mark me as inactive
        active.current = false
        // if i only have one dataset, pick it
        const myDataset = reader.datasets.length == 1 ? reader.datasets[0] : null
        // and use it to initialize my dataset of choice
        dataset.current = myDataset
        // reset my selector
        selector.current = new Map()
        // and my channel
        channel.current = null
    }

    // if there is a dataset choice
    if (dataset.current) {
        // use it to initialize my selector
        selector.current = new Map(
            // by going through its coordinate settings and flattening them into key/value pairs
            dataset.current.selector.map(({ name, value }) => [name, value])
        )
        // if it only has one channel
        if (dataset.current.channels.length == 1) {
            channel.current = dataset.current.channels[0]
        }
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
    }

    // provide for my children
    return (
        <Context.Provider value={context} >
            {props.children}
        </Context.Provider >
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
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
