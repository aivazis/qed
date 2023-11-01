// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { useCollapseViewport } from '../explorer/useCollapseViewport'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, } from './buttons'
import { Local } from './local'
import { S3 } from './s3'
import { TypeSelector } from './type'
import { Form, Body } from '../form'


// the form
export const Archive = ({ view, viewport }) => {
    // make some room for the archive type
    const [type, setType] = React.useState(null)
    // make a handler that collapses this viewport
    const hide = useCollapseViewport(viewport)
    // build a selector with the correct signature
    const update = (field, value) => {
        // set the value
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
        // remove the view in my viewport from the pile
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
                        <TypeSelector value={type} update={update} />
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

// the dispatch table with the archive types
const types = {
    local: Local,
    s3: S3,
}


// end of file