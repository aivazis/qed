// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// locals
// hooks
import { useViewports } from '~/views/viz'
// styles
import styles from './styles'


// remove a {viewport} from the {viz} panel
export const Selector = ({ viewport, view }) => {
    // get the active view
    const { activeViewport } = useViewports()
    // unpack the view
    const { reader, dataset, channel } = useFragment(selectorViewerGetViewFragment, view)
    // get the name of the reader
    const name = reader?.name
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
            {name && <span style={paint.separator}>&middot;</span>}
            {/* the dataset selector */}
            {selector.map(binding => (
                <React.Fragment key={`${binding.name}`}>
                    <span style={paint.selector}>{binding.value}</span>
                    <span style={paint.separator}>&middot;</span>
                </React.Fragment>
            ))}
            {/* the channel name */}
            <span style={paint.selector}>{channel.tag}</span>
        </span>
    )
}


// my fragment
const selectorViewerGetViewFragment = graphql`
    fragment selectorViewerGetViewFragment on View {
        reader {
            name
        }
        dataset {
            selector {
                name
                value
            }
        }
        channel {
            tag
        }
    }
`


// end of file