// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// hooks
import { useRange } from './useRange'
// components
import { Less } from './less'
import { More } from './more'
// styles
import styles from './styles'


// turn the panel into a context provider and publish
export const Table = ({ min = 0, initial = 0, max = 0, ...rest }) => {
    // set up the context provider
    return (
        <Provider min={min} initial={initial} max={max} >
            <Panel {...rest} />
        </Provider >
    )
}


// setup a container for displaying metadata
const Panel = ({ style, children, ...rest }) => {
    // get the detail range
    const { min, max } = useRange()
    // mix my paint
    const tableStyle = { ...styles.box, ...style?.box }
    const detailStyle = { ...styles.detail.box, ...style?.detail?.box }
    // render
    return (
        <table style={tableStyle} {...rest}>
            {min != max &&
                <thead>
                    <tr>
                        <th colSpan="3" style={detailStyle} >
                            detail:
                            <Less />
                            |
                            <More />
                        </th>
                    </tr>
                </thead>
            }
            <tbody>
                {children}
            </tbody>
            {min != max &&
                <tfoot>
                    <tr>
                        <th colSpan="3" style={detailStyle}></th>
                    </tr>
                </tfoot>
            }
        </table >
    )
}


// end of file