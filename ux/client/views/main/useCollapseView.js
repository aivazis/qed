// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from './useViewports'


// remove a viewport
export const useCollapseView = () => {
    // get the active viewport
    const { activeViewport, setActiveViewport } = useViewports()
    // collapsing a view mutates the server side application store
    const [request, pending] = useMutation(collapseMutation)

    // make a handler that removes a viewport
    const collapse = viewport => {
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
                const response = store.getRootField("collapseView")
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
                // all done
                return
            },
            // when the request is complete
            onCompleted: data => {
                // if the active viewport has collapsed or the active viewport is after the
                // collapsed one on the pile
                if (viewport <= activeViewport) {
                    // activate the previous one
                    setActiveViewport(Math.max(viewport - 1, 0))
                }
                // all done
                return
            },
            // if something goes wrong
            onError: error => {
                // show me
                console.log(`views.main.useCollapseView: ERROR while collapsing ${viewport}:`, error)
                // all done
                return
            }
        })
        // all done
        return
    }

    // and return it
    return collapse
}


// the mutation that collapses a viewport
const collapseMutation = graphql`
    mutation useCollapseViewMutation($viewport: Int!) {
        collapseView(viewport: $viewport) {
            views {
                id
            }
        }
    }
`


// end of file
