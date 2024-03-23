// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from './useViewports'


// split a viewport
export const useSplitView = () => {
    // get the active viewport setter
    const { setActiveViewport } = useViewports()
    // splitting a view mutates the server side application store
    const [request, pending] = useMutation(splitMutation)

    // make a handler that splits a viewport in two
    const split = viewport => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                viewport
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewSplit")
                // ask for the list of views
                const updated = response.getLinkedRecords("views")
                // if it's trivial
                if (updated === null) {
                    // something went wrong at the server; not much more to do
                    return
                }
                // get the remote store
                const qed = store.get("QED")
                // attach the updated pile
                qed.setLinkedRecords(updated, "views")
            },
            // when the request is complete
            onCompleted: data => {
                // activate the new view
                setActiveViewport(viewport + 1)
                // all done
                return
            },
            // if something goes wrong
            onError: error => {
                // show me
                console.log(`views.main.useSplitView: ERROR while splitting ${viewport}:`, error)
                // all done
                return
            }
        })
        // all done
        return
    }
    // and return it
    return split
}


// the mutation that splits a viewport
const splitMutation = graphql`
    mutation useSplitViewMutation($viewport: Int!) {
        viewSplit(viewport: $viewport) {
            views {
                id
            }
        }
    }
`



// end of file
