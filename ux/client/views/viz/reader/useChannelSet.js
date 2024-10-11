// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// project
// hooks
import { useViewports } from '~/views/viz'

// local
// context
import { useReader } from './useReader'


// toggle the {tag} as the value for {channel}
export const useChannelSet = channel => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(channelSetMutation)

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
                selection: {
                    viewport,
                    reader: reader.name,
                    selector: "channels",
                    value: channel.tag,
                }
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.reader.useChannelSet:`)
                console.group()
                console.error(`ERROR while toggling '${reader.name}, channel${channel.tag}'`)
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


// the mutation that selects a reader
const channelSetMutation = graphql`
    mutation useChannelSetMutation($selection: ViewSelectorInput!) {
        viewChannelSet(selection: $selection) {
            views {
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
                # for the flow layer
                ...flowVizGetFlowDiagramFragment
                ...flowViewerGetFlowLayerStateFragment
                # for the measure layer control
                ...measureViewerGetMeasureLayerStateFragment
                # for the sync control
                ...syncViewerGetScrollSyncStateFragment
                # for the measure control
                ...measureControlsGetMeasureLayerStateFragment
                ...minimapControlsGetMeasureLayerStateFragment
                ...profileMeasureGetMeasureLayerFragment
                # for the print button
                ...printViewerGetViewFragment
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
