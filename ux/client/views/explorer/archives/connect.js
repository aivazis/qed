// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useConnectArchive } from './useConnectArchive'
import { useGetActiveView } from '../explorer/useGetActiveView'
// shapes
import { Plus as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// components
import {
    // top level
    Form,
    // containers
    Body, Footer, Row,
    // items
    Prompt, Separator, Value, Required,
} from '../form'
// styles
import { connect as paintConnect } from './styles'


// control to connect a new data archive
export const Connect = () => {
    // get the activator
    const collectArchiveInfo = useConnectArchive()
    // connect a new archive
    const connect = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // collect the new archive info
        collectArchiveInfo()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: connect,
    }
    // render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={paintConnect}>
            <Icon />
        </Badge>

    )
}


export const Info = () => {
    // render
    return (
        <Table>
            <Body>
                <ArchiveTypes />
            </Body>
            <Footer>

            </Footer>

        </Table>
    )
}

// override of the form component
const Table = styled(Form)`
    font-size: 70%;
    padding-top: 1.0em;
`

// support for selecting table types
const ArchiveTypes = () => {
    // unpack the active view
    const { newArchive } = useGetActiveView()
    // render
    return (
        <Row>
            <Prompt>
                {newArchive.uri === null && <Required>*</Required>}
                uri
            </Prompt>
            <Separator>:</Separator>
            <Value>
            </Value>
        </Row>
    )
}


// end of file