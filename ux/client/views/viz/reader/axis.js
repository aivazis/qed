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
import { useSelector } from './useSelector'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Axis = ({ axis, children }) => {
    // get the current selector
    const selector = useSelector()
    // make a label that is marked as required when when there is no selection for this {axis}
    const label = (
        <span>
            {selector.has(axis)
                ? null
                : <span style={styles.required}>*</span>
            }
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
