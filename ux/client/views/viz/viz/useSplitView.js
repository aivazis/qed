// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
                // ask for the view
                const view = response.getLinkedRecord("view")
                // if it's trivial
                if (view === null) {
                    // something went wrong at the server; not much more to do
                    return
                }
                // get the remote store
                const qed = store.get("QED")
                // get the views
                const views = qed.getLinkedRecords("views")
                // update
                const updated = views.toSpliced(viewport + 1, 0, view)
                // attach the new view
                qed.setLinkedRecords(updated, "views")
                // all done
                return
            },
            // when the request is complete
            onCompleted: data => {
                // activate the new view
                setActiveViewport(viewport + 1)
                // all done
                return
            },
            // if something goes wrong
            onError: errors => {
                // show me
                console.log(`views.main.useSplitView:`)
                console.group()
                console.log(`ERROR while splitting ${viewport}:`)
                console.log(errors)
                console.groupEnd()
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
            view {
                id
                # for synchronized scrolling
                ...vizGetScrollSyncedViewsFragment
                # for the measure layer
                ...measureGetMeasureLayerFragment
                # for the viewport
                ...viewportViewerGetViewFragment
                # for the info widget with the dataset metadata
                ...infoViewerGetViewFragment
                # whatever readers need
                ...contextReaderGetViewFragment
                # for the measure layer control
                ...measureViewerGetMeasureLayerStateFragment
                # for the sync control
                ...syncViewerGetScrollSyncStateFragment
                # for the print button
                ...printViewerGetViewFragment
                # for the measure control
                ...measureControlsGetMeasureLayerStateFragment
                ...minimapControlsGetMeasureLayerStateFragment
                ...profileMeasureGetMeasureLayerFragment
                # for the zoom control
                ...zoomControlsGetZoomStateFragment
                # for the viz control
                ...vizControlsGetViewFragment
                # for the sync table
                ...bodyGetViewSyncStateFragment
            }
        }
    }
`



// end of file
