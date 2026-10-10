// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// components
import { Connectors } from '../connectors'
import { Labels } from '../labels'
import { Factories } from './factories'
import { Grid } from './grid'
import { Slots } from './slots'


// a diagram seen from above, in layers: the cell under the cursor, the labels, the connectors,
// the slots, and the factories on top
export const FlatScene = ({ diagram }) => {
    // render
    return (
        <>
            {/* the current cell highlighter */}
            <Grid />
            {/* labels */}
            <Labels diagram={diagram} />
            {/* connectors */}
            <Connectors diagram={diagram} />
            {/* slots */}
            <Slots diagram={diagram} />
            {/* factories */}
            <Factories diagram={diagram} />
        </>
    )
}


// end of file
