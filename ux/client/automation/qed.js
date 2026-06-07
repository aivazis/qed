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


// the model read: each view's reader, channel, zoom, measure path, and selectors, in the same
// row-major source-pixel coordinates the markup publishes
const stateQuery = graphql`
    query qedStateQuery {
        qed {
            views {
                reader { name }
                dataset { shape origin channels { tag } }
                channel { tag }
                zoom { vertical horizontal }
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
    zoom: view.zoom && { vertical: view.zoom.vertical, horizontal: view.zoom.horizontal },
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

    // select {tag} as the channel of {viewport}; the input also carries the reader, so resolve it first
    setChannel: async (tag, viewport = activeViewport) => {
        const { qed } = await read(stateQuery)
        const reader = qed.views[viewport]?.reader?.name
        return command(channelSetMutation, { viewport, reader, value: tag })
    },

    // the measure layer
    measure: {
        // clear the path of {viewport}
        reset: (viewport = activeViewport) => command(resetMeasureMutation, { viewport }),
    },
})


// end of file
