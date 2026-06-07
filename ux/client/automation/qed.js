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
    state: async (viewport = getActiveViewport()) => {
        const { qed } = await read(stateQuery)
        return modelOf(qed.views[viewport], viewport)
    },

    // the model of every viewport, for split layouts
    viewports: async () => {
        const { qed } = await read(stateQuery)
        return qed.views.map((view, index) => modelOf(view, index))
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

    // make {viewport} the active one (the facade default and, via the bridge, the ui)
    setActive: viewport => activate(viewport),

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
        // set {viewport}'s relative sync offset to {row,col} source pixels
        updateOffset: (row, col, viewport = getActiveViewport()) =>
            command(syncUpdateOffsetMutation, { viewport, x: col, y: row }),
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
    },
})


// end of file
