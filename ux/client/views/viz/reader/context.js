// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql } from 'relay-runtime'
import { useFragment } from 'react-relay/hooks'


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
                shape
                origin
                datatype
                selector {
                    name
                    value
                }
                channels
            }
        }`,
        props.reader
    )

    // if the reader has only one dataset, select it automatically
    const singleton = reader.datasets.length === 1 ? reader.datasets[0] : null
    // initialize the dataset choice
    const [dataset, setDataset] = React.useState(singleton)
    // initialize the selector, a map { axis } -> { coordinate } that reflects the current choice
    const [selector, setSelector] = React.useState(new Map())
    // initialize the channel
    const [channel, setChannel] = React.useState(null)

    // assemble the context value
    const context = {
        // the reader info
        reader,
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
        // the reader info
        reader: null,
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
