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


// set the per-member participation mask of a stack
export const useSetMembers = () => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // adjusting membership mutates the server side store
    const [commit, pending] = useMutation(setMembersMutation)

    // make the handler; {members} is the full per-member boolean mask
    const setMembers = (members, viewport = activeViewport) => {
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
                members,
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewSetMembers")
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
                console.error(`viz.reader.useSetMembers:`)
                console.group()
                console.error(`ERROR while setting the membership of '${reader.name}'`)
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
    return setMembers
}


// the mutation that sets the per-member participation mask
const setMembersMutation = graphql`
    mutation useSetMembersMutation($viewport: Int!, $source: String!, $members: [Boolean!]!) {
        viewSetMembers(viewport: $viewport, source: $source, members: $members) {
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


/* end of file */
