// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Info } from '~/widgets'

// locals
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Selector = ({ attribute, value }) => {

    // render
    return (
        <Info name={attribute} value={value} style={styles.selectors} />
    )
}


// end of file