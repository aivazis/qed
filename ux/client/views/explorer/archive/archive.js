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
import {
    // top level
    Form,
    // containers
    Body, Footer, Row,
    // items
    Prompt, Separator, Value, Required,
} from '../form'
import { Cancel, EnabledConnect, DisabledConnect, } from './buttons'
import { Local } from './local'
import { S3 } from './s3'
import { TypeSelector } from './type'


// the form
export const Archive = ({ view, viewport }) => {
    // make some room for the archive type
    const [type, setType] = React.useState(null)
    // make a handler that collapses this viewport
    const collapseViewport = useCollapseViewport(viewport)
    // build a selector with the correct signature
    const update = (field, value) => {
        // set the value
        setType(value)
        // all done
        return
    }
    // build a handler that cancels the new archive connection
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // remove the view in my viewport from the pile
        collapseViewport()
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
                    <Footer>
                    </Footer>
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
        <Connector setType={update} cance={cancel} />
    )
}

// the dispatch table with the archive types
const types = {
    local: Local,
    s3: S3,
}


// the editor panel
const Panel = styled.div`
    font-size: 70%;
    padding: 1.0rem 0.0 0.5rem 0.0em;
    // border-top: 1px solid hsl(0, 0%, 15%);
    // border-bottom: 1px solid hsl(0, 0%, 15%);
    // background-color: hsl(0deg, 0%, 7%);
`


// end of file