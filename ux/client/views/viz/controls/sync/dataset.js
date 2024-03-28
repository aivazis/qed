// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from '~/palette'

// locals
// hooks
import { useViewports } from '~/views/viz'
// components
import { Cell } from './cell'

// the body of the sync control table
export const Dataset = ({ viewport, children }) => {
    // get the active viewport and the active viewport selector
    const { activeViewport, activate } = useViewports()

    // if this is the active viewport
    if (viewport === activeViewport) {
        // render the selected dataset
        return (
            <SelectedDataset>
                {children}
            </SelectedDataset>
        )
    }

    // otherwise, build a handler to activate this viewport
    const select = activate(viewport)
    // wrap it in an event hadler
    const click = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash any side effects
        evt.preventDefault()
        // activate this viewport
        select()
        // all done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: click,
    }
    // and render an active dataset
    return (
        <ActiveDataset {...behaviors}>
            {children}
        </ActiveDataset>
    )
}


// the styles
const ActiveDataset = styled(Cell)`
    font-family: inconsolata;
    font-size: 110%;
    text-align: left;
    overflow: auto;
    cursor: pointer;
`

const SelectedDataset = styled(ActiveDataset)`
    color: ${() => theme.page.highlight};
    cursor: default;
`


// end of file