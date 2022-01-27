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
import { useChannel } from './useChannel'
import { useGetView } from '../viz/useGetView'
import { useVisualize } from '../viz/useVisualize'
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
    // the selected channel
    const channel = useChannel()
    // and its mutator
    const visualize = useVisualize()

    // schedule an update of the current view
    React.useEffect(() => {
        // if i'm the active reader
        if (active) {
            // with my accumulated state
            visualize({ reader, dataset, channel })
        }
    },
        // every time my potential contribution to the active view changes
        [active, dataset, channel]
    )

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

    // set up my controls
    let behaviors = {}
    // if am enabled
    if (state == "enabled") {
        // handler that makes me the active reader
        const select = evt => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // quash the default behavior
            evt.preventDefault()
            // make me the active reader
            visualize({ reader, dataset, channel })
            // all done
            return
        }
        // adjust my controllers
        behaviors = {
            // whatever i had before
            ...behaviors,
            // plus click to select
            onClick: select,
        }
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


// end of file
