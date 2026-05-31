// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from '~/views/viz'

// the provider factory
export const Provider = props => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get the active view
    const view = useFragment(contextReaderGetViewFragment, props.views[activeViewport])

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
    // the effective availability: a pinned member realizes more combos than the aggregate, so
    // when i'm the active reader use the view's availability, otherwise my own collective set
    const available = new Map(
        (active ? view.available : reader.available).map(
            selector => [selector.name, new Set(selector.values)]
        )
    )
    // convert the user selections into a (axis -> value) map
    const selections = new Map(
        view.selections.map(selection => [selection.name, selection.value])
    )
    // if i am a stack, the number of members i have
    const stackExtent = reader.stackExtent
    // the pinned member, but only meaningful when i am the active reader
    const stackIndex = active ? view.stackIndex : null

    // assemble the context value
    const context = {
        // my details, as harvested from the server
        reader,
        // the dataset
        dataset,
        // the channel
        channel,
        // my state
        active,
        // the table of possible choices for each selector axis
        available,
        // the current set of user choices
        selections,
        // the number of members if i am a stack
        stackExtent,
        // my pinned member, if i am the active reader
        stackIndex,
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
// the information necessary for manipulating the set of viewable panels
// must get at least as much as it takes to feed the dataset selection
export const contextReaderGetViewFragment = graphql`
    fragment contextReaderGetViewFragment on View {
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
        selections {
            name
            value
        }
        stackIndex
        available {
            name
            values
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
        available {
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
        stackExtent
    }
`

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
