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
import { useResetZoomMutation as resetZoomMutation } from '~/views/viz/controls/zoom/useReset'
import { useLookAtMutation as lookAtMutation } from '~/views/viz/viewer/useLookAt'
import { useSyncToggleAllMutation as syncToggleAllMutation } from '~/views/viz/controls/sync/useSyncToggleAll'
import { useUpdateRangeControllerMutation as updateRangeControllerMutation } from '~/views/viz/controls/viz/useUpdateRangeController'
import { useResetRangeControllerMutation as resetRangeControllerMutation } from '~/views/viz/controls/viz/useResetRangeController'
import { useUpdateValueControllerMutation as updateValueControllerMutation } from '~/views/viz/controls/viz/useUpdateValueController'
import { useResetValueControllerMutation as resetValueControllerMutation } from '~/views/viz/controls/viz/useResetValueController'
import { useAnchorAddMutation as anchorAddMutation } from '~/views/viz/measure/useAnchorAdd'
import { useAnchorPlaceMutation as anchorPlaceMutation } from '~/views/viz/measure/useAnchorPlace'
import { useAnchorSplitMutation as anchorSplitMutation } from '~/views/viz/measure/useAnchorSplit'
import { useAnchorRemoveMutation as anchorRemoveMutation } from '~/views/viz/measure/useAnchorRemove'
import { measureToggleLayerMutation } from '~/views/viz/measure/useMeasureToggleLayer'
import { useToggleClosedPathMutation as toggleClosedPathMutation } from '~/views/viz/measure/useToggleClosedPath'
import { useAnchorToggleSelectionMutation as anchorToggleSelectionMutation } from '~/views/viz/measure/useAnchorToggleSelection'
import { useAnchorToggleSelectionMultiMutation as anchorToggleSelectionMultiMutation } from '~/views/viz/measure/useAnchorToggleSelectionMulti'
import { useAnchorExtendSelectionMutation as anchorExtendSelectionMutation } from '~/views/viz/measure/useAnchorExtendSelection'
import { selectReaderMutation } from '~/views/viz/reader/useSelectReader'
import { toggleCoordinateMutation } from '~/views/viz/reader/useToggleCoordinate'
// the store updater the reader/coordinate mutations share, since they swap the whole view
import { replaceViewUpdater } from '~/views/viz/reader/replaceView'
import { splitMutation } from '~/views/viz/viz/useSplitView'
import { collapseMutation } from '~/views/viz/viz/useCollapseView'
import { splitViewUpdater, collapseViewUpdater } from '~/views/viz/viz/viewListUpdaters'
import { useSyncToggleViewportMutation as syncToggleViewportMutation } from '~/views/viz/controls/sync/useSyncToggleViewport'
import { useSyncUpdateOffsetMutation as syncUpdateOffsetMutation } from '~/views/viz/controls/sync/useSyncUpdateOffset'
// the active viewport, kept in sync with the ui by the {ViewportBridge}
import { getActiveViewport, activate } from './activeViewport'


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

// the name of the channel shown in {viewport}; the controller inputs key on it (the server uses the
// channel name, not its display tag)
const channelOf = async viewport => {
    const { qed } = await read(stateQuery)
    return qed.views[viewport]?.channel?.name
}


// the model read: each view's reader, channel, zoom, measure path, and selectors, in the same
// row-major source-pixel coordinates the markup publishes
const stateQuery = graphql`
    query qedStateQuery {
        qed {
            views {
                reader { name }
                dataset { shape origin channels { tag } }
                channel { tag name }
                zoom { vertical horizontal coupled }
                measure { active closed path { x y } selection }
                sync { scroll channel zoom path }
                available { name values }
            }
        }
    }
`

// the reader catalog: every reader the server offers and the selector axes it binds
const readersQuery = graphql`
    query qedReadersQuery {
        qed {
            readers { name selectors { name values } }
        }
    }
`

// the colour-stretch controllers bound to a viewport's channel; {__typename} tells a range controller
// from a value one
const controllersQuery = graphql`
    query qedControllersQuery {
        qed {
            views { channel { controllers { __typename slot min max } } }
        }
    }
`

// the sync reset has no ui control, so the facade carries its own document; the returned {sync}
// auto-merges by its node id
const syncResetMutation = graphql`
    mutation qedSyncResetMutation($input: ViewSyncResetInput!) {
        viewSyncReset(input: $input) {
            sync { dirty scroll channel zoom path }
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
    state: async (viewport = getActiveViewport()) => {
        const { qed } = await read(stateQuery)
        return modelOf(qed.views[viewport], viewport)
    },

    // the model of every viewport, for split layouts
    viewports: async () => {
        const { qed } = await read(stateQuery)
        return qed.views.map((view, index) => modelOf(view, index))
    },

    // the reader catalog: each reader's name and its selector axes, keyed by axis name
    readers: async () => {
        const { qed } = await read(readersQuery)
        return (qed.readers ?? []).map(reader => ({
            name: reader.name,
            selectors: Object.fromEntries((reader.selectors ?? []).map(axis => [axis.name, axis.values])),
        }))
    },

    // the colour-stretch controllers on {viewport}'s channel: each one's kind (range|value), slot,
    // and bounds, so a driver picks one by kind and feeds it to {range}/{value}
    controllers: async (viewport = getActiveViewport()) => {
        const { qed } = await read(controllersQuery)
        return (qed.views[viewport]?.channel?.controllers ?? []).map(controller => ({
            kind: controller.__typename.replace(/Controller$/, "").toLowerCase(),
            slot: controller.slot, min: controller.min, max: controller.max,
        }))
    },

    // select the reader named {reader} for {viewport}; swapping the view needs the shared updater
    selectReader: (reader, viewport = getActiveViewport()) =>
        command(selectReaderMutation, { viewport, reader },
            replaceViewUpdater("viewReaderSelect", viewport)),

    // toggle {value} of the {selector} axis (band/frequency/polarization) for {viewport}; the input
    // also carries the reader, and swapping the view needs the shared updater
    selectValue: async (selector, value, viewport = getActiveViewport()) =>
        command(toggleCoordinateMutation,
            { viewport, reader: await readerOf(viewport), selector, value },
            replaceViewUpdater("viewCoordinateToggle", viewport)),

    // select {tag} as the channel of {viewport}; the input also carries the reader
    setChannel: async (tag, viewport = getActiveViewport()) =>
        command(channelSetMutation, { viewport, reader: await readerOf(viewport), value: tag }),

    // set the zoom of {viewport}; a number applies to both axes, an object sets them independently
    setZoom: (level, viewport = getActiveViewport()) => {
        const { vertical, horizontal } = typeof level === "object"
            ? level : { vertical: level, horizontal: level }
        return command(setLevelZoomMutation, { viewport, vertical, horizontal })
    },

    // flip whether the two zoom axes move together on {viewport}
    toggleCoupled: (viewport = getActiveViewport()) => command(toggleCoupledZoomMutation, { viewport }),

    // reset {viewport} to its default zoom
    zoomReset: (viewport = getActiveViewport()) => command(resetZoomMutation, { viewport }),

    // make {viewport} the active one (the facade default and, via the bridge, the ui)
    setActive: viewport => activate(viewport),

    // scroll {viewport} so the source pixel {row,col} sits at the center of the visible window. this
    // moves the local DOM scroll directly -- like a user dragging -- reading the rendered zoom off the
    // region markup and converting source pixels to rendered ones. the viewport's scroll handler turns
    // that into a {viewLookAt} mutation, so the move now also syncs to every other client
    centerOn: (row, col, viewport = getActiveViewport()) => new Promise(resolve => {
        const region = document.querySelectorAll('[data-qed-region="viewport"]')[viewport]
        if (region == null) {
            resolve()
            return
        }
        const [vertical, horizontal] = region.getAttribute("data-qed-zoom").split(",").map(Number)
        region.scrollLeft = col * 2 ** horizontal - region.clientWidth / 2
        region.scrollTop = row * 2 ** vertical - region.clientHeight / 2
        // resolve once the scroll has had a frame to apply and notify the pan dispatcher
        requestAnimationFrame(() => resolve())
    }),

    // set the look-at center of {viewport} to the source pixel {row,col} directly through the server,
    // bypassing the local scroll; every client (this one included, over live sync) recenters there.
    // this is the deterministic path for automation -- no scroll throttle to wait on
    lookAt: (row, col, viewport = getActiveViewport()) =>
        command(lookAtMutation, { viewport, row, col }),

    // split {viewport} in two; the new view lands after it and becomes active, as in the ui
    split: async (viewport = getActiveViewport()) => {
        await command(splitMutation, { viewport }, splitViewUpdater(viewport))
        activate(viewport + 1)
    },

    // remove {viewport}; the active viewport retreats if it was at or past it, as in the ui
    collapse: async (viewport = getActiveViewport()) => {
        await command(collapseMutation, { viewport }, collapseViewUpdater(viewport))
        if (viewport <= getActiveViewport()) activate(Math.max(viewport - 1, 0))
    },

    // scroll synchronization
    sync: {
        // flip the {aspect} (scroll/channel/zoom/path) sync flag of {viewport}
        toggle: (aspect, viewport = getActiveViewport()) =>
            command(syncToggleViewportMutation, { viewport, aspect }),
        // flip the {aspect} flag across every viewport, using {viewport} as the reference
        toggleAll: (aspect, viewport = getActiveViewport()) =>
            command(syncToggleAllMutation, { viewport, aspect }),
        // set {viewport}'s relative sync offset to {row,col} source pixels
        updateOffset: (row, col, viewport = getActiveViewport()) =>
            command(syncUpdateOffsetMutation, { viewport, x: col, y: row }),
        // reset {viewport}'s sync flags and offset
        reset: (viewport = getActiveViewport()) => command(syncResetMutation, { viewport }),
    },

    // the measure layer; {row,col} are source pixels, translated here to the mutations' {x,y}
    measure: {
        // show or hide the layer of {viewport}; the input carries the reader
        toggle: async (viewport = getActiveViewport()) =>
            command(measureToggleLayerMutation, { viewport, reader: await readerOf(viewport) }),
        // clear the path of {viewport}
        reset: (viewport = getActiveViewport()) => command(resetMeasureMutation, { viewport }),
        // append an anchor at {row,col}, or insert it at {index}
        add: (row, col, index = null, viewport = getActiveViewport()) =>
            command(anchorAddMutation, { viewport, x: col, y: row, index }),
        // move anchor {handle} to {row,col}
        move: (handle, row, col, viewport = getActiveViewport()) =>
            command(anchorPlaceMutation, { viewport, handle, x: col, y: row }),
        // insert an anchor on the segment after {handle}
        split: (handle, viewport = getActiveViewport()) =>
            command(anchorSplitMutation, { viewport, anchor: handle }),
        // delete anchor {handle}
        remove: (handle, viewport = getActiveViewport()) =>
            command(anchorRemoveMutation, { viewport, anchor: handle }),
        // close or open the path of {viewport}
        toggleClosedPath: (viewport = getActiveViewport()) =>
            command(toggleClosedPathMutation, { viewport }),
        // toggle anchor {handle} in the selection (replacing it)
        toggleSelection: (handle, viewport = getActiveViewport()) =>
            command(anchorToggleSelectionMutation, { viewport, index: handle }),
        // toggle anchor {handle} in the selection (adding to it)
        toggleSelectionMulti: (handle, viewport = getActiveViewport()) =>
            command(anchorToggleSelectionMultiMutation, { viewport, index: handle }),
        // extend the selection through anchor {handle}
        extendSelection: (handle, viewport = getActiveViewport()) =>
            command(anchorExtendSelectionMutation, { viewport, index: handle }),
    },

    // the colour-stretch range controller of a {channel} (defaulting to the active one); {controller}
    // names which one, and the bounds are {min,low,high,max}
    range: {
        update: async (controller, { min, low, high, max }, channel, viewport = getActiveViewport()) =>
            command(updateRangeControllerMutation,
                { viewport, channel: channel ?? await channelOf(viewport), controller, min, low, high, max }),
        reset: async (controller, channel, viewport = getActiveViewport()) =>
            command(resetRangeControllerMutation,
                { viewport, channel: channel ?? await channelOf(viewport), controller }),
    },

    // the colour-stretch value controller of a {channel}; the bounds are {min,value,max}
    value: {
        update: async (controller, { min, value, max }, channel, viewport = getActiveViewport()) =>
            command(updateValueControllerMutation,
                { viewport, channel: channel ?? await channelOf(viewport), controller, min, value, max }),
        reset: async (controller, channel, viewport = getActiveViewport()) =>
            command(resetValueControllerMutation,
                { viewport, channel: channel ?? await channelOf(viewport), controller }),
    },
})


// end of file
