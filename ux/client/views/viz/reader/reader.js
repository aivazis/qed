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
// context
import { Provider } from './context'
// hooks
import { useReader } from './useReader'
import { useIsActive } from './useIsActive'
import { useDataset } from './useDataset'
import { useUpdateView } from './useUpdateView'
// components
import { Axis } from './axis'
import { Channels } from './channels'
// styles
import styles from './styles'


// turn the panel into a context provider and publish
export const Reader = props => (
    <Provider {...props}>
        <Panel />
    </Provider>
)


// display the datasets associated with this reader
const Panel = () => {
    // get my details
    const reader = useReader()
    // my state marker
    const active = useIsActive()
    // the selected dataset, if any
    const dataset = useDataset()
    // get the view update
    const update = useUpdateView()

    // unpack the reader
    const { id, uri, selectors } = reader
    // parse the reader id; ignore the {family} name that is not used here
    const [, name] = id.split(":")
    // if i have a valid dataset selection, grab its channels
    const channels = dataset?.channels ?? []

    // deduce my state; for me, things are simple:
    // - i exist, so i can't be {disabled}
    // - therefore i'm always {enabled}
    // - no one asks me questions, so i'm never {available}
    // - {selected} iff in {view}, which is checked as part of my {context} initialization
    const state = active ? "selected" : "enabled"

    // set up my controllers
    const behaviors = {
        // click to select
        onClick: update,
    }

    // mix my paint
    const paint = styles.reader(state)
    // and render
    return (
        <Tray title={name} initially={true} state={state}>
            <Meta.Table style={paint.meta} {...behaviors}>
                {null &&
                    <Meta.Entry attribute="uri" style={paint.meta}>
                        {uri}
                    </Meta.Entry>
                }
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


// end of file
