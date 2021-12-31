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

    // am i the active view?
    const amActive = idx === activeView
    // get my view info
    const { reader, dataset, channel } = views[idx]

    // grab my style
    const tabStyle = styles.tab
    // mix my piant
    // for the dataset name
    const datasetStyle = {
        ...tabStyle.dataset,
        ...(amActive ? tabStyle.active : null)
    }
    // for selectors and channels
    const selectorStyle = {
        ...tabStyle.selector,
        ...(amActive ? tabStyle.active : null)
    }

    // render
    return (
        <div style={tabStyle.box}>
            <Badge size={8} state="available" behaviors={collapse} style={tabStyle.collapse} >
                <X style={tabStyle.collapse} />
            </Badge>
            <div style={datasetStyle}>{reader?.name}</div>
            {reader && <div style={tabStyle.separator}>:</div>}
            {dataset?.selector.map(binding => (
                <React.Fragment key={`${binding.name}.name`} >
                    <div style={selectorStyle}>{binding.value}</div>
                    <div style={tabStyle.separator}>:</div>
                </React.Fragment>
            ))}
            <div style={selectorStyle}>{channel}</div>
            <Badge size={12} state="available" behaviors={split} style={tabStyle.split} >
                <Split style={tabStyle.split} />
            </Badge>
        </div>
    )
}


// end of file