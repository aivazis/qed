// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// routing
import { Outlet } from 'react-router-dom'


// project
// hooks
import { useActivityPanel } from '~/views'
// widgets
import { Flex } from '~/widgets'

// local
// components
import Welcome from './welcome.mdx'
// paint
import { flex, toc } from './styles'


// the panel
export const Guide = () => {
    // the activity panel state
    const { activityPanel } = useActivityPanel()

    // mix my paint
    // copy the toc paint
    const tocPaint = { ...toc }
    // so we can hide it when its not visible
    tocPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={flex}>
            {/* the table of contents */}
            <Flex.Panel min={300} style={tocPaint}>
                <Outlet />
            </Flex.Panel>

            {/* the panel with the current page */}
            <Flex.Panel style={flex}>
                <Welcome />
            </Flex.Panel>

        </Flex.Box>
    )

}


// end of file
