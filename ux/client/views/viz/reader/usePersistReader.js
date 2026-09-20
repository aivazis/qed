// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// write the reader called {name} into the configuration files
export const usePersistReader = name => {
    // build the mutation request
    const [request, isInFlight] = useMutation(usePersistReaderMutation)
    // build the handler
    const persist = () => {
        // if a request is already on its way
        if (isInFlight) {
            // there is nothing to do
            return
        }
        // send the mutation to the server; saving changes nothing the client displays, so
        // there is nothing to merge and no updater is necessary
        request({
            // input
            variables: {
                input: { name }
            },
        })
        // all done
        return
    }
    // hand off the handler, and whether a request is on its way
    return { persist, isInFlight }
}


// the mutation, exported so the automation facade can commit the same document
export const usePersistReaderMutation = graphql`
    mutation usePersistReaderMutation($input: PersistReaderInput!) {
        persistReader(input: $input) {
            reader {
                id
            }
        }
    }
`


// end of file
