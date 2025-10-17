// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
import { useSelectReader } from './useSelectReader'
// components
import { Axis } from './axis'
import { Channels } from './channels'
import { Disconnect } from './disconnect'
// styles
import styles from './styles'


// turn the panel into a context provider and publish
export const Reader = ({ qed, ...props }) => (
    <Provider {...props}>
        <Panel qed={qed} />
    </Provider >
)


// display the datasets associated with this reader
const Panel = ({ qed }) => {
    // get my details
    const reader = useReader()
    // my state marker
    const active = useIsActive()
    // the selected dataset, if any
    const dataset = useDataset()
    // get the view update
    const select = useSelectReader()

    // unpack the reader
    const { name, uri, selectors } = reader
    // if i have a valid dataset selection, grab its channels
    const channels = dataset?.channels ?? []

    // deduce my state; for me, things are simple:
    // - i exist, so i can't be {disabled}
    // - therefore i'm always {enabled}
    // - no one asks me questions, so i'm never {available}
    // - {selected} iff in {view}, which is checked as part of my {context} initialization
    const state = active ? "selected" : "enabled"

    // turn select into an event handler
    const selectReader = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // modify the server side store
        select()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        // click to select
        onClick: selectReader,
    }
    // build my controls
    const Controls = <Disconnect qed={qed} name={name} />

    // mix my paint
    const paint = styles.reader(state)
    // and render
    return (
        <Tray title={name} initially={true} state={state} scale={0.5} controls={Controls}>
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
                {channels.length > 0 && <Channels>{channels}</Channels>}
            </Meta.Table>
        </Tray>
    )
}


// end of file
