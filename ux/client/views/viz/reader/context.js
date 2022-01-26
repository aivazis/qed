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

    // the active view
    const view = useGetView()
    // make some room for my default initial state
    let active = false
    // if there i have only one dataset, select it
    let iDataset = null
    // and if it only has one channel, prime my channel as well
    let iChannel = null

    // if i'm being rendered after a {view} has been selected, and i happen to be the reader
    // in the active view
    if (reader.uuid === view?.reader?.uuid) {
        // mark me as the active reader
        active = true
        // if the active view has a selected dataset
        if (view.dataset) {
            // it must be mine
            iDataset = view.dataset
        }
        // if the active view has a selected channel
        if (view.channel) {
            // save it
            iChannel = view.channel
        }
    }
    // if didn't get a dataset selection from the current view and i only have one
    if (!iDataset && reader.datasets.length === 1) {
        // select it automatically
        iDataset = reader.datasets[0]
    }
    // if i didn't get a channel selection from the current view and the selected dataset only
    // has a single channel
    if (!iChannel && iDataset && iDataset.channels.length === 1) {
        // select it
        iChannel = iDataset.channels[0]
    }
    // initialize my selector
    const iSelector = new Map(
        // if i have a selected dataset
        iDataset
            // unpack its selector
            ? iDataset.selector.map(({ name, value }) => [name, value])
            // make an empty one
            : []
    )

    // initialize the dataset choice
    const [dataset, setDataset] = React.useState(iDataset)
    // initialize the selector, a map { axis } -> { coordinate } that reflects the current choice
    const [selector, setSelector] = React.useState(iSelector)
    // initialize the channel
    const [channel, setChannel] = React.useState(iChannel)

    // assemble the context value
    const context = {
        // my details, as harvested from the server
        reader,
        // my state
        active,
        // the dataset
        dataset, setDataset,
        // the selector
        selector, setSelector,
        // the channel
        channel, setChannel,
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
        setDataset: () => { throw new Error(complaint) },
        // the selector
        selector: null,
        setSelector: () => { throw new Error(complaint) },
        // the channel
        channel: null,
        setChannel: () => { throw new Error(complaint) },
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
