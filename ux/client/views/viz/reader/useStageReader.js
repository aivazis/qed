// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// ask the server to make first contact with one data source
// this is the retry affordance of a source whose survey failed: the same verb that stages
// the catalog, pointed at a single product
export const useStageReader = (name) => {
    // build the mutation request
    const [request, isInFlight] = useMutation(stageMutation)
    // assemble the handler
    const stage = () => {
        // if a request is already on its way
        if (isInFlight) {
            // let it finish
            return
        }
        // otherwise, ask the server to survey this product again
        request({
            // the payload names the one source to stage
            variables: { input: { reader: name } },
        })
        // all done
        return
    }
    // hand off the handler and the flag that says a request is pending
    return { stage, isInFlight }
}


// the request that initiates first contact with a single source
const stageMutation = graphql`
    mutation useStageReaderMutation($input: StageInput!) {
        stage(input: $input) {
            readers {
                id
                name
                status
                error
            }
        }
    }
`


// end of file
