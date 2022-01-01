// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Skull } from '~/shapes'
// styles
import styles from './styles'


// kill the server
const activity = ({ size, style }) => {
    // paint me
    return (
        <Activity size={size} url="/stop" barStyle={style} style={styles} >
            <Skull />
        </Activity >
    )
}


// publish
export default activity


// end of file
