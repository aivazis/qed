// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// graphql
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viz' context: no provider"

// setup the flex context
export const VizContext = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the known views
        views: [],
        setView: () => { throw new Error(complaint) },
        // the synced views
        synced: null,
        setSynced: () => { throw new Error(complaint) },
        // the active view
        activeView: null,
        setActiveView: () => { throw new Error(complaint) },

        // the readers
        readers: null,
    }
)


// the provider factory
export const VizProvider = ({
    // children
    children
}) => {
    // setup the views; a views is an object with a fully resolved dataset selector
    const [views, setViews] = React.useState(new Array())
    // a table with the sync status of the known views
    const [synced, setSynced] = React.useState(new Map())
    // the active view is an index into the {views}
    const [activeView, setActiveView] = React.useState(0)

    // ask the server for the collection of known datasets
    const { readers: knownReaders } = useLazyLoadQuery(contextQuery)
    // set up the readers
    const [readers] = React.useState(knownReaders)

    // build the current value of the context
    const context = {
        // the views
        views, setViews,
        // synced views
        synced, setSynced,
        // active view
        activeView, setActiveView,
        // readers
        readers,
    }

    // provide for my children
    return (
        <VizContext.Provider value={context} >
            {children}
        </VizContext.Provider >

    )
}


// the dataset query
const contextQuery = graphql`query contextQuery {
    readers(first: 100) @connection(key: "datasets_readers") {
        count
        edges {
            node {
                # {datasets} needs the {uuid} to make the keys for its children
                uuid
                # plus whatever the {reader} needs to render itself
                ...reader_reader
            }
            cursor
        }
    }
}`


// end of file
