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
import { Hammer } from '~/shapes'
// styles
import styles from './styles'


// sandbox for experimenting with new features
const activity = ({ size, style }) => {
    // paint me
    return (
        <Activity size={size} url="/graphiql" barStyle={style} style={styles} >
            <Hammer />
        </Activity >
    )
}


// publish
export default activity


// end of file
