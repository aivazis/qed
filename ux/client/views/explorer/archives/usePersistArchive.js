// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// write the archive at {uri} into the configuration files
export const usePersistArchive = () => {
    // build the mutation request
    const [request, isInFlight] = useMutation(usePersistArchiveMutation)
    // build the handler
    const handler = ({ uri }) => {
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
                input: { uri }
            },
        })
        // all done
        return
    }
    // hand off the handler, and whether a request is on its way
    return { persist: handler, isInFlight }
}


// the mutation, exported so the automation facade commits the same document
export const usePersistArchiveMutation = graphql`
    mutation usePersistArchiveMutation($input: PersistArchiveInput!) {
        persistArchive(input: $input) {
            archive {
                id
            }
        }
    }
`


// end of file
