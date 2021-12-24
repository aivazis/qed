// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Badge } from '~/widgets'
// locals
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Channel = ({ dataset, channel }) => {

    // mix the styles
    const boxStyle = styles.channel.box
    const nameStyle = styles.channel.name

    // render
    return (
        <div style={boxStyle}>
            <div style={nameStyle}>{channel}</div>
        </div>
    )
}


// end of file