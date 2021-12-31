// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'


// project
// shapes
import { Split, X } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useViews } from './useViews'
import { useCollapseView } from './useCollapseView'
import { useSplitView } from './useSplitView'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Tab = ({ idx }) => {
    // get the views
    const { activeView, views } = useViews()
    // make a handler that splits this view
    const split = { onClick: useSplitView(idx) }
    // and one that collapses this view
    const collapse = { onClick: useCollapseView(idx) }

    // get my view info
    const { reader, dataset, channel } = views[idx]

    // grab my style
    const tabStyle = styles.tab

    // render
    return (
        <div style={tabStyle.box}>
            <Badge size={12} state="available" behaviors={collapse} style={tabStyle.dismiss} >
                <X />
            </Badge>
            <div style={tabStyle.dataset}>{reader?.name}</div>
            {reader && <div style={tabStyle.separator}>:</div>}
            {dataset?.selector.map(binding => (
                <React.Fragment key={`${binding.name}.name`} >
                    <div style={tabStyle.selector}>{binding.value}</div>
                    <div style={tabStyle.separator}>:</div>
                </React.Fragment>
            ))}
            <div style={tabStyle.selector}>{channel}</div>
            <Badge size={12} state="available" behaviors={split} style={tabStyle.split} >
                <Split style={tabStyle.split} />
            </Badge>
        </div>
    )
}


// end of file