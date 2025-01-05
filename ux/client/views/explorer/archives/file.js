// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useSelectDataset } from './useSelectDataset'
// styles
import { file as paintFile } from './styles'

// the panel with the directory contents
export const File = ({ name, uri }) => {
    // deduce my state and behavior
    const { state, selector } = useSelectDataset({ name, uri })

    // mix my paint
    const paint = paintFile(state)
    // render
    return (
        <div style={paint} onClick={selector} title={uri}>
            {name}
        </div>
    )
}


// end of file
