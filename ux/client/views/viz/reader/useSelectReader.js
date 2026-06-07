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
// hooks
import { useReader } from './useReader'
// the shared store updater
import { replaceViewUpdater } from './replaceView'


// select the reader that's active in a viewport
export const useSelectReader = () => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(selectReaderMutation)

    // make the handler
    const select = (viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            // input
            variables: {
                // the payload
                input: {
                    viewport,
                    reader: reader.name
                }
            },
            // update the store: selecting a reader swaps the whole view
            updater: replaceViewUpdater("viewReaderSelect", viewport),
            onError: errors => {
                // show me
                console.log(`viz.reader.useSelectReader:`)
                console.group()
                console.log(`ERROR while selecting '${reader.name}':`)
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
    return select
}

// the mutation that selects a reader; exported so the {window.qed} automation facade can commit it
export const selectReaderMutation = graphql`
    mutation useSelectReaderMutation($input: ViewReaderSelectInput!) {
        viewReaderSelect(input: $input) {
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