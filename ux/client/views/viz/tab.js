// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'


// project
// widgets
import { Spacer } from '~/widgets'

// locals
// components
import { Collapse } from './collapse'
import { Split } from './split'
import { Sync } from './sync'
// hooks
import { useViews } from './useViews'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Tab = ({ idx, view, behaviors }) => {
    // get the active view
    const { activeView } = useViews()
    // am i the active view?
    const amActive = idx === activeView
    // get my view info
    const { reader, dataset, channel } = view

    // grab my style
    const tabStyle = styles.tab
    // mix my paint
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
        <div style={tabStyle.box} {...behaviors} >
            {/* the button that removes this view from the panel */}
            <Collapse view={idx} />

            {/* the fully resolved selector */}
            <div style={datasetStyle}>{reader?.name}</div>
            {reader && <div style={tabStyle.separator}>:</div>}
            {dataset?.selector.map(binding => (
                <React.Fragment key={`${binding.name}.name`} >
                    <div style={selectorStyle}>{binding.value}</div>
                    <div style={tabStyle.separator}>:</div>
                </React.Fragment>
            ))}
            <div style={selectorStyle}>{channel}</div>

            {/* some blank space */}
            <Spacer />
            {/* the button that adds a new view to the {viz} panel */}
            <Split view={idx} />
            {/* the button that toggles the sync status of the data viewport */}
            <Sync viewport={idx} />
        </div>
    )
}


// end of file