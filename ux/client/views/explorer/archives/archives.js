// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
            <Header title="data archives" style={headerPaint}>
                <Connect />
            </Header>
            {/* go through the repositories and render them */}
            {archives.map(archive => (
                <Archive key={archive.name} archive={archive} />
            ))}
        </>
    )
}


// end of file
