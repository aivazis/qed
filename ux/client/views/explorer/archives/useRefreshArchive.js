// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// list every folder on display of the archive at {uri} again
export const useRefreshArchive = () => {
    // build the mutation request
    const [request, isInFlight] = useMutation(useRefreshArchiveMutation)
    // build the handler
    const handler = ({ uri }) => {
        // send the mutation to the server; the payload carries the archive tree, which relay
        // merges into the archive record, so no updater is necessary
        request({
            // input
            variables: {
                input: { uri }
            },
        })
        // all done
        return
    }
    // hand off the handler
    return handler
}


// the mutation, exported so the automation facade commits the same document
export const useRefreshArchiveMutation = graphql`
    mutation useRefreshArchiveMutation($input: RefreshArchiveInput!) {
        refreshArchive(input: $input) {
            archive {
                id
                expanded
                pending
                error
                hits
                dirty
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`


// end of file
