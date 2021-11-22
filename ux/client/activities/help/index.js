// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Help } from '~/shapes'
// styles
import styles from './styles'


// show the embedded documentation
const activity = ({ size, style }) => {
    // paint me
    return (
        <Activity size={size} url="/help" barStyle={style} style={styles} >
            <Help />
        </Activity >
    )
}


// publish
export default activity


// end of file
