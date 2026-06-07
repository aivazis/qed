// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { commitMutation, fetchQuery, graphql } from 'react-relay'

// the live relay environment, so commands update the store exactly as the ui controls do, with no
// reload; see {doc/automation-surface.md}
import { environment } from '~/environment'
// mutation documents reused verbatim from the hooks the ui uses, so the store updates identically
import { channelSetMutation } from '~/views/viz/reader/useChannelSet'
import { resetMeasureMutation } from '~/views/viz/controls/measure/useReset'
import { useSetLevelZoomMutation as setLevelZoomMutation } from '~/views/viz/controls/zoom/useSetLevel'
import { useToggleCoupledZoomMutation as toggleCoupledZoomMutation } from '~/views/viz/controls/zoom/useToggleCoupled'
import { useAnchorAddMutation as anchorAddMutation } from '~/views/viz/measure/useAnchorAdd'
import { useAnchorPlaceMutation as anchorPlaceMutation } from '~/views/viz/measure/useAnchorPlace'
import { useAnchorSplitMutation as anchorSplitMutation } from '~/views/viz/measure/useAnchorSplit'
import { useAnchorRemoveMutation as anchorRemoveMutation } from '~/views/viz/measure/useAnchorRemove'
import { measureToggleLayerMutation } from '~/views/viz/measure/useMeasureToggleLayer'


// the viewport a command targets when the caller names none; kept current by {setActiveViewport},
// the bridge mounted inside the viewports provider. defaults to the lone viewport the app boots with
let activeViewport = 0
export const setActiveViewport = viewport => { activeViewport = viewport }


// commit {mutation} with the single {input} every qed mutation takes and resolve once it settles;
// {updater} is the optional store-shaping a ui hook would apply for mutations relay cannot auto-merge
const command = (mutation, input, updater) => new Promise((resolve, reject) => {
    commitMutation(environment, {
        mutation,
        variables: { input },
        updater,
        onCompleted: (response, errors) => (errors?.length ? reject(errors) : resolve(response)),
        onError: reject,
    })
})

// read {query} and resolve with its data, populating the store as a side effect
const read = (query, variables = {}) => fetchQuery(environment, query, variables).toPromise()

// the name of the reader bound to {viewport}; several inputs (channel, measure toggle) carry it
const readerOf = async viewport => {
    const { qed } = await read(stateQuery)
    return qed.views[viewport]?.reader?.name
}


// the model read: each view's reader, channel, zoom, measure path, and selectors, in the same
// row-major source-pixel coordinates the markup publishes
const stateQuery = graphql`
    query qedStateQuery {
        qed {
            views {
                reader { name }
                dataset { shape origin channels { tag } }
                channel { tag }
                zoom { vertical horizontal coupled }
                measure { active closed path { x y } selection }
                sync { scroll channel zoom path }
                available { name values }
            }
        }
    }
`

// reshape one raw {view} record into the facade's model, translating column-major {x,y} pixels to
// the row-major {row,col} the rest of qed reports
const modelOf = (view, viewport) => view == null ? null : ({
    viewport,
    reader: view.reader?.name ?? null,
    dataset: view.dataset && {
        shape: view.dataset.shape,
        origin: view.dataset.origin,
        channels: (view.dataset.channels ?? []).map(channel => channel.tag),
    },
    channel: view.channel?.tag ?? null,
    selectors: Object.fromEntries((view.available ?? []).map(axis => [axis.name, axis.values])),
    zoom: view.zoom && {
        vertical: view.zoom.vertical, horizontal: view.zoom.horizontal, coupled: view.zoom.coupled,
    },
    measure: view.measure && {
        active: view.measure.active,
        closed: view.measure.closed,
        path: (view.measure.path ?? []).map(pixel => ({ row: pixel.y, col: pixel.x })),
        selection: view.measure.selection ?? [],
    },
    sync: view.sync && {
        scroll: view.sync.scroll, channel: view.sync.channel,
        zoom: view.sync.zoom, path: view.sync.path,
    },
})


// assemble the facade published at {window.qed}
export const makeQED = () => ({
    // the model of {viewport}, or null when it does not exist
    state: async (viewport = activeViewport) => {
        const { qed } = await read(stateQuery)
        return modelOf(qed.views[viewport], viewport)
    },

    // select {tag} as the channel of {viewport}; the input also carries the reader
    setChannel: async (tag, viewport = activeViewport) =>
        command(channelSetMutation, { viewport, reader: await readerOf(viewport), value: tag }),

    // set the zoom of {viewport}; a number applies to both axes, an object sets them independently
    setZoom: (level, viewport = activeViewport) => {
        const { vertical, horizontal } = typeof level === "object"
            ? level : { vertical: level, horizontal: level }
        return command(setLevelZoomMutation, { viewport, vertical, horizontal })
    },

    // flip whether the two zoom axes move together on {viewport}
    toggleCoupled: (viewport = activeViewport) => command(toggleCoupledZoomMutation, { viewport }),

    // the measure layer; {row,col} are source pixels, translated here to the mutations' {x,y}
    measure: {
        // show or hide the layer of {viewport}; the input carries the reader
        toggle: async (viewport = activeViewport) =>
            command(measureToggleLayerMutation, { viewport, reader: await readerOf(viewport) }),
        // clear the path of {viewport}
        reset: (viewport = activeViewport) => command(resetMeasureMutation, { viewport }),
        // append an anchor at {row,col}, or insert it at {index}
        add: (row, col, index = null, viewport = activeViewport) =>
            command(anchorAddMutation, { viewport, x: col, y: row, index }),
        // move anchor {handle} to {row,col}
        move: (handle, row, col, viewport = activeViewport) =>
            command(anchorPlaceMutation, { viewport, handle, x: col, y: row }),
        // insert an anchor on the segment after {handle}
        split: (handle, viewport = activeViewport) =>
            command(anchorSplitMutation, { viewport, anchor: handle }),
        // delete anchor {handle}
        remove: (handle, viewport = activeViewport) =>
            command(anchorRemoveMutation, { viewport, anchor: handle }),
    },
})


// end of file
