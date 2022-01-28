// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widget
import { Meta } from '~/widgets'

// locals
// components
import { Coordinate } from './coordinate'
// hooks
import { useIsActive } from './useIsActive'
import { useSelector } from './useSelector'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Axis = ({ axis, children }) => {
    // get the selection status of my reader
    const active = useIsActive()
    // the current selector
    const selector = useSelector()

    // a mark is required if my reader is the active one and the selector has no value for me
    const mark = active && !selector.get(axis)
    // make a label that is marked as required when when there is no selection for this {axis}
    const label = (
        <span>
            {mark ? <span style={styles.mark}>*</span> : null}
            {axis}
        </span>
    )

    // mix my paint
    const paint = styles.axis()
    // and render
    return (
        <Meta.Entry attribute={label} style={paint}>
            {children.map(coordinate => (
                <Coordinate key={coordinate} axis={axis} coordinate={coordinate} />
            ))}
        </Meta.Entry>
    )
}


// end of file
