// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// styles
import styles from './styles'


// export the data viewport
const Panel = ({ viewport, view, uri, registrar, ...rest }) => {
    // nothing yet
    return null
}


// context
import { Provider } from './context'
// turn the panel into a context provider and publish
export const Viewport = props => (
    <Provider>
        <Panel {...props} />
    </Provider>
)


// end of file
