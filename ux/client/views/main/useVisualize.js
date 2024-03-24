// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from './useViewports'


// hook that adjusts the contents of a given viewport
// currently, only called by {reader} instances when selected/updated
export const useVisualize = () => {
    // grab the active viewport index and the {views} mutator
    const { activeViewport } = useViewports()
    // placing a view in a viewport mutates the server side application store
    const [request, pending] = useMutation(visualizeMutation)

    // make the handler
    const visualize = (view, viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, place the, possible partial, view information in the server side store
        request({
            // input
            variables: {
                // the payload
                viewport: viewport,
                reader: view?.reader?.name || null,
                dataset: view?.dataset?.name || null,
                channel: view?.channel?.tag || null,
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewUpdate")
                // ask for the view
                const view = response.getLinkedRecord("view")
                //if it's trivial
                if (view == null) {
                    // something went wrong at the server; bail, for now
                    return
                }
                // if all is good, get the remote store
                const qed = store.get("QED")
                // get the views
                const views = qed.getLinkedRecords("views")
                // replace the view at {viewport} with the new one
                qed.setLinkedRecords(views.toSpliced(viewport, 1, view), "views")
                // all done
                return
            },
            // if something goes wrong
            onError: error => {
                // show me
                console.log(`main.useVisualize: ERROR:`, error)
            }

        })
        // all done
        return
    }

    // and return it
    return visualize
}


// the mutation that places a view in a viewport
const visualizeMutation = graphql`
    mutation useVisualizeMutation(
        $viewport: Int!, $reader: String, $dataset: String, $channel: String
    ) {
        viewUpdate(reader: $reader, dataset: $dataset, channel: $channel, viewport: $viewport) {
            view {
                id
                name
            }
        }
    }
`

// end of file
