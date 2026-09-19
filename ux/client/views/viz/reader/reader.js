// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


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
import { usePreparing } from './usePreparing'
// components
import { Axis } from './axis'
import { Channels } from './channels'
import { Stack } from './stack'
import { Standing } from './standing'
import { Disconnect } from './disconnect'
import { Retry } from './retry'
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
    // whether my dataset is still being prepared
    const preparing = usePreparing()

    // unpack the reader
    const { name, uri, status, selectors } = reader
    // my selectors and channels describe a product that has been opened; until then, they
    // would be offering choices that lead nowhere
    const ready = status === "ready"
    // a product that could not be opened flags its tray, so the trouble shows when collapsed
    const failed = status === "failed"
    // and one that is still being opened shows that work is under way
    const opening = !ready && !failed
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
        // modify the server side store, if necessary
        if (!active) {
            // by selecting me if i'm not the active reader
            select()
        }
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        // click to select
        onClick: selectReader,
    }
    // build my controls: a product that could not be opened offers another attempt, next to
    // the control that lets go of the reader
    const Controls = (
        <>
            {failed && <Retry name={name} />}
            <Disconnect qed={qed} name={name} />
        </>
    )

    // mix my paint
    const paint = styles.reader(state)
    // and render; the reader carries its name as client identity so its selectors are addressable
    // per reader (two readers can share an axis, e.g. {frequency}), forwarded onto the {Tray} section
    return (
        <Tray title={name} initially={true} state={state} scale={0.5} controls={Controls}
            alert={failed} busy={opening} data-qed-reader={name}>
            <Meta.Table style={paint.meta} {...behaviors}>
                <Meta.Entry attribute="uri" style={paint.meta}>
                    {uri}
                </Meta.Entry>
                {/* what the source is doing, while it is not yet viewable */}
                <Standing style={paint.meta} />
                {ready && selectors.map(selector => {
                    // unpack
                    const { name: axis, values } = selector
                    // build an axis and return it
                    return <Axis key={axis} axis={axis}>{values}</Axis>
                })}
                {ready && <Stack />}
                {/* the channels appear when the dataset is worth looking at; offering them while
                    the viewport is still waiting would promise something the view cannot show */}
                {ready && channels.length > 0 && !preparing && <Channels>{channels}</Channels>}
            </Meta.Table>
        </Tray>
    )
}


// end of file
