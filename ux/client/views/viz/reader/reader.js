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
import { useGetView } from '../viz/useGetView'
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
    // and the active view
    const view = useGetView()

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
    // mix my paint
    const paint = styles.reader(state)

    // render
    return (
        <Tray title={name} initially={state === "selected"} style={paint.tray} >
            <Meta.Table style={paint.meta}>
                <Meta.Entry attribute="uri" style={paint.meta}>{uri}</Meta.Entry>
                <Meta.Entry attribute="reader" style={paint.meta}>{family}</Meta.Entry>
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
