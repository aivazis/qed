// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Header } from '~/widgets'

// locals
//hooks
import { useArchives } from '../explorer/useArchives'
// components
import { Archive } from './archive'
import { Connect } from '../archive'
// styles
import { header as headerPaint } from './styles'


// the panel with the known data archives
export const Archives = () => {
    // get the repositories
    const archives = useArchives()
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="data archives" style={headerPaint} controls={<Connect />} />
            {/* go through the repositories and render them */}
            {archives.edges.map(edge => (
                <Archive key={edge.node.name} archive={edge.node} />
            ))}
        </>
    )
}


// end of file
