// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a widget that can act as a header or a title
export const Info = ({ name, value, style }) => {
    // mix my styles
    const infoStyle = { ...styles.info, ...style?.info }
    const nameStyle = { ...styles.name, ...style?.name }
    const valueStyle = { ...styles.value, ...style?.value }
    const separatorStyle = { ...styles.separator, ...style?.separator }

    // paint me
    return (
        <div style={infoStyle} >
            <span style={nameStyle}>{name}</span>
            <span style={separatorStyle}>:</span>
            <span style={valueStyle}>{value}</span>
        </div>
    )
}


// end of file
