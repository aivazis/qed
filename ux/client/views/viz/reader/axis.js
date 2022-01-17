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
import { useReader } from './useReader'
import { useSelector } from './useSelector'
import { useGetView } from '../viz/useGetView'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Axis = ({ axis, children }) => {
    // get my reader
    const reader = useReader()
    // the current selector
    const selector = useSelector()
    // and the current view
    const view = useGetView()

    // a mark is required if my reader is the current one and the selector has no value for me
    const required = view?.reader?.uuid === reader.uuid && !selector.has(axis)
    // make a label that is marked as required when when there is no selection for this {axis}
    const label = (
        <span>
            {required ? <span style={styles.required}>*</span> : null}
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
