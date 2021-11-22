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
import { Flame } from '~/shapes'
// styles
import styles from './styles'


// visualize
const activity = ({ size, style }) => {
    // paint me
    return (
        <Activity size={size} url="/about" barStyle={style} style={styles} >
            <Flame />
        </Activity >
    )
}


// publish
export default activity


// end of file
