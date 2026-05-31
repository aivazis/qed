// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// project
// hooks
import { useViewports } from '~/views/viz'

// local
// context
import { useReader } from './useReader'


// pin a stack member, or clear the pin to return to the collective aggregate view
export const useSetStackIndex = () => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // pinning a member mutates the server side store
    const [commit, pending] = useMutation(setStackIndexMutation)

    // make the handler; pass {index} null to clear the pin
    const setStackIndex = (index, viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            // input
            variables: {
                viewport,
                source: reader.name,
                index,
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewSetStackIndex")
                // ask for the view
                const view = response.getLinkedRecord("view")
                // if it's trivial
                if (view === null) {
                    // something went wrong at the server; not much more to do
                    return
                }
                // get the remote store
                const qed = store.get("QED")
                // get the current set of views
                const views = qed.getLinkedRecords("views")
                // replace the view at {viewport} with the new one
                qed.setLinkedRecords(views.toSpliced(viewport, 1, view), "views")
                // all done
                return
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.reader.useSetStackIndex:`)
                console.group()
                console.error(`ERROR while pinning '${reader.name}' to member '${index}'`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }

    // all done
    return setStackIndex
}


// the mutation that pins or clears a stack member
const setStackIndexMutation = graphql`
    mutation useSetStackIndexMutation($viewport: Int!, $source: String!, $index: Int) {
        viewSetStackIndex(viewport: $viewport, source: $source, index: $index) {
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
