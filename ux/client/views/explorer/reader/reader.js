// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useCollapseViewport } from '../explorer/useCollapseViewport'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect } from './buttons'
import { Type } from './type'
import { Form, Body } from '../form'
// reader types
import { GDAL } from './gdal'
import { ISCE2 } from './isce2'
import { NISAR } from './nisar'


// the form
export const Reader = ({ view, viewport }) => {
    // make room for the reader type
    const [type, setType] = React.useState(null)
    // make a handler that collapses this viewport
    const hide = useCollapseViewport(viewport)
    // build a selector with the generic signature
    const update = (field, value) => {
        // set the type
        setType(value)
        // all done
        return
    }
    // build a handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // remove the form from view
        hide()
        // all done
        return
    }
    // if we don't have a type selection yet
    if (type === null) {
        // render
        return (
            <Panel>
                <Form>
                    <Body>
                        <Type value={type} update={update} />
                    </Body>
                </Form>
                <DisabledConnect />
                <Cancel onClick={cancel}>cancel</Cancel>
            </Panel>
        )
    }
    // otherwise, resolve the connector
    const Connector = types[type]
    // and render it
    return (
        <Connector view={view} setType={update} hide={hide} />
    )
}


// the dispatch table with the reader types
const types = {
    gdal: GDAL,
    isce2: ISCE2,
    nisar: NISAR,
}


// end of file
