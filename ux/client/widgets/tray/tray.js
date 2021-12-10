// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
import { Indicator } from './indicator'
// styles
import styles from './styles'


// a tray with a header and some items
export const Tray = ({ title, style, children }) => {
    // storage for my state
    const [expanded, setExpanded] = React.useState(false)

    // handler for flipping my state
    const toggle = () => setExpanded(!expanded)

    // mix my paint
    const boxStyle = { ...styles.box, ...style?.box }
    const headerStyle = { ...styles.header, ...style?.header }
    const titleStyle = { ...styles.title, ...style?.title }
    const itemsStyle = { ...styles.items, ...style?.items }

    // paint me
    return (
        <section style={boxStyle} >
            <div style={headerStyle} onClick={toggle}>
                <Indicator expanded={expanded} />
                <span style={titleStyle} >
                    {title}
                </span>
            </div>
            <div style={itemsStyle} >
                {expanded && children}
            </div>
        </section>
    )
}


// end of file
