// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
import { Selector } from './selector'


// display the selectors associated with this dataset
export const Selectors = ({ selector }) => {
    // render
    return (
        <>
            {selector.map(({name, value}) => (
                <Selector key={name} attribute={name} value={value} />
            ))}
        </>
    )
}


// end of file