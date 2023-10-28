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
    Body, Footer, Row, Panel,
    // items
    Prompt, Separator, Value, Required,
    // buttons
    Cancel,
} from '../form'
import { TypeSelector } from './type'


// the form
export const Archive = ({ view, viewport }) => {
    console.log(viewport, view)
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
                <Table>
                    <Body>
                        <TypeSelector value={type} update={update} />
                    </Body>
                    <Footer>
                    </Footer>
                </Table>
                <Cancel onClick={cancel}>cancel</Cancel>
            </Panel>
        )
    }
    // otherwise, do stuff
    return null
}

// override of the form component
const Table = styled(Form)`
    font-size: 70%;
    padding-top: 1.0em;
`


// end of file