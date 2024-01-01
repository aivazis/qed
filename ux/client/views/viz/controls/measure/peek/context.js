// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useDatasetShape } from '../../../viz/useDatasetShape'


// the provider factory
export const Provider = ({ children }) => {
    // get the name and extent of its dataset
    const { name: dataset, origin, shape } = useDatasetShape()

    // query state management
    const [loading, setLoading] = React.useState(false)
    // query options
    const [options, setOptions] = React.useState()
    // and query variables
    const [variables, setVariables] = React.useState({
        dataset,
        line: origin[0],
        sample: origin[1],
    })

    // build the initial context value
    const context = {
        // record the dataset information
        dataset, origin, shape,
        // query state management
        loading, setLoading,
        // options
        options, setOptions,
        // and variables
        variables, setVariables,
    }

    // provide from my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider>
    )
}


// set up the {peek} context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // dataset
        dataset: null, origin: null, shape: null,
        // query state
        loading: null,
        setLoading: () => { throw new Error(complaint) },
        // options
        options: null,
        setOptions: () => { throw new Error(complaint) },
        // variables
        variables: null,
        setVariables: () => { throw new Error(complaint) },
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'peek' context: no provider"


// end of file
