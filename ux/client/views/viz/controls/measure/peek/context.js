// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import { graphql, useFragment } from 'react-relay'


// the provider factory
export const Provider = ({ view, children }) => {
    // unpack the view
    const { dataset } = useFragment(contextPeekMeasureGetDatasetFragment, view)
    // extract what i need
    const { name, origin, shape } = dataset
    // query state management
    const [loading, setLoading] = React.useState(false)
    // query options
    const [options, setOptions] = React.useState(null)
    // and query variables
    const [variables, setVariables] = React.useState({
        dataset: name,
        line: origin[0],
        sample: origin[1],
    })

    // build the initial context value
    const context = {
        // record the dataset information
        dataset: name, origin, shape,
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


// the fragment
const contextPeekMeasureGetDatasetFragment = graphql`
    fragment contextPeekMeasureGetDatasetFragment on View {
        dataset {
            name
            origin
            shape
        }
    }
`


// end of file
