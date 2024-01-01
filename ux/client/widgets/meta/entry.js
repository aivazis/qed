// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// hooks
import { useDetail } from './useDetail'
// locals
import styles from './styles'


// an individual entry
export const Entry = ({ threshold = 0, attribute, style, children }) => {
    // get the current detail level
    const { detail } = useDetail()
    // if my threshold is higher
    if (threshold > detail) {
        // show nothing
        return null
    }

    // mix my paint
    const entryStyle = { ...styles.entry, ...style?.entry }
    const attributeStyle = { ...styles.attribute, ...style?.attribute }
    const separatorStyle = { ...styles.separator, ...style?.separator }
    const valueStyle = { ...styles.value, ...style?.value }

    // paint me
    return (
        <tr style={entryStyle}>
            <td style={attributeStyle}>{attribute}</td>
            <td style={separatorStyle}>:</td>
            <td style={valueStyle}>
                {children}
            </td>
        </tr>
    )
}


// end of file
