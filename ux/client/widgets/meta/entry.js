// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// an individual entry
export const Entry = ({ attribute, style, children }) => {
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
