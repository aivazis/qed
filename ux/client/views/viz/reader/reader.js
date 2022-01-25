// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Meta, Tray } from '~/widgets'

// locals
// hooks
import { useReader } from './useReader'
import { useDataset } from './useDataset'
import { useChannel } from './useChannel'
import { useGetView } from '../viz/useGetView'
import { useVisualize } from '../viz/useVisualize'
// components
import { Axis } from './axis'
import { Channels } from './channels'
// styles
import styles from './styles'


// display the datasets associated with this reader
const Panel = () => {
    // get my reader
    const reader = useReader()
    // the selected dataset, if any
    const dataset = useDataset()
    // the selected channel
    const channel = useChannel()
    // the active view
    const view = useGetView()
    // and its mutator
    const visualize = useVisualize()

    // unpack the reader
    const { id, uuid, uri, selectors } = reader
    // parse the reader id
    const [family, name] = id.split(":")
    // if i have a valid dataset selection, grab its channels
    const channels = dataset?.channels ?? []

    // deduce my state; for me, things are simple:
    // - i exist, so i can't be {disabled}
    // - therefore i'm always {enabled}
    // - no one asks me questions, so i'm never {available}
    // - {selected} iff in {view}
    const state = (uuid === view?.reader?.uuid) ? "selected" : "enabled"

    // handler that make me the active reader
    const select = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // if i'm already the current viewer
        if (state === "selected") {
            // bail
            return
        }
        // otherwise, make me the active view
        visualize({ reader, dataset, channel })
        // all done
        return
    }
    // assemble my controllers
    const behaviors = {
        // click to select
        onClick: select,
    }

    // mix my paint
    const paint = styles.reader(state)
    // and render
    return (
        <Tray title={name} initially={state === "selected"} style={paint.tray}>
            <Meta.Table style={paint.meta} {...behaviors}>
                <Meta.Entry attribute="uri" style={paint.meta}>
                    {uri}
                </Meta.Entry>
                {selectors.map(selector => {
                    // unpack
                    const { name: axis, values } = selector
                    // build an axis and return it
                    return <Axis key={axis} axis={axis}>{values}</Axis>
                })}
                <Channels>{channels}</Channels>
            </Meta.Table>
        </Tray>
    )
}


// context
import { Provider } from './context'
// turn the panel into a context provider and publish
export const Reader = props => (
    <Provider {...props}>
        <Panel />
    </Provider>
)


// end of file
