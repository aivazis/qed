// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { RelayConcreteNode } from 'relay-runtime'

// locals
// hooks
import { useViews } from '../viz/useViews'
// styles
import styles from './styles'


// remove a {viewport} from the {viz} panel
export const Selector = ({ viewport, view }) => {
    // get the active view
    const { activeViewport } = useViews()

    // unpack the view
    const { reader, dataset, channel } = view
    // get the name of the reader
    const [_, name] = reader.id.split(":")
    // and the dataset selector
    const selector = dataset?.selector ?? []

    // deduce my state
    const state = (viewport === activeViewport) ? "selected" : "enabled"
    // mix my paint
    const paint = styles.selector(state)
    // and render
    return (
        <span style={paint.box}>
            {/* the name of the dataset source */}
            {name && <span style={paint.name}>{name}</span>}
            {/* a separator */}
            {name && <span style={paint.separator}>:</span>}
            {/* the dataset selector */}
            {selector.map(binding => (
                <React.Fragment key={`${binding.name}`}>
                    <span style={paint.selector}>{binding.value}</span>
                    <span style={paint.separator}>:</span>
                </React.Fragment>
            ))}
            {/* the channel name */}
            <span style={paint.selector}>{channel}</span>
        </span>
    )
}


// end of file