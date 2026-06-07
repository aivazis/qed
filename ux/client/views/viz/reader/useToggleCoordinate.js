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
// the shared store updater
import { replaceViewUpdater } from './replaceView'


// toggle the {coordinate} as the value for {axis}
export const useToggleCoordinate = (axis, coordinate) => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(toggleCoordinateMutation)

    // make the handler
    const toggle = (viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            //input
            variables: {
                // the payload
                input: {
                    viewport,
                    reader: reader.name,
                    selector: axis,
                    value: coordinate,
                }
            },
            // update the store: toggling a coordinate swaps the whole view
            updater: replaceViewUpdater("viewCoordinateToggle", viewport),
            onError: errors => {
                // send the error to the console
                console.error(`viz.reader.useToggleCoordinate:`)
                console.group()
                console.error(`ERROR while toggling '${reader.name}:${axis}:${coordinate}'`)
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
    return toggle
}


// the mutation that toggles a coordinate; exported so the {window.qed} automation facade can commit it
export const toggleCoordinateMutation = graphql`
    mutation useToggleCoordinateMutation($input: ViewCoordinateToggleInput!) {
        viewCoordinateToggle(input: $input) {
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
