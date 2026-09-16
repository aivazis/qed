// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// expand the folder at {uri} of the archive at {archive}
export const useExpandFolder = () => {
    // build the mutation request
    const [request, isInFlight] = useMutation(useExpandFolderMutation)
    // build the handler
    const handler = ({ archive, uri }) => {
        // send the mutation to the server; the payload carries the archive tree, which relay
        // merges into the archive record, so no updater is necessary
        request({
            // input
            variables: {
                input: { archive, uri }
            },
        })
        // all done
        return
    }
    // hand off the handler
    return handler
}


// the mutation, exported so the automation facade commits the same document
export const useExpandFolderMutation = graphql`
    mutation useExpandFolderMutation($input: ExpandFolderInput!) {
        expandFolder(input: $input) {
            archive {
                id
                expanded
                pending
                error
                hits
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
