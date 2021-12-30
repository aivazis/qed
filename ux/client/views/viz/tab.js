// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'


// project
// shapes
import { X } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useViews } from './useViews'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Tab = ({ idx }) => {
    // get the views
    const { activeView, views } = useViews()

    // get my view info
    const { reader, dataset, channel } = views[idx]

    console.log(dataset.selector)

    // render
    return (
        <div style={styles.tab.box}>
            <Badge size={12} state="available" style={styles.tab.dismiss} >
                <X />
            </Badge>
            <div style={styles.tab.dataset}>{reader.name}</div>
            <div style={styles.tab.separator}>:</div>
            {dataset.selector.map(binding => (
                <React.Fragment key={`${binding.name}.name`} >
                    <div style={styles.tab.selector}>{binding.value}</div>
                    <div style={styles.tab.separator}>:</div>
                </React.Fragment>
            ))}
            <div style={styles.tab.selector}>{channel}</div>
        </div>
    )
}


// end of file