// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// components
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Name } from './name'
import { Path } from './path'
import { Form, Body, Footer, } from '../form'

// a data archive local to the qed server
export const Local = ({ updateURI, setType, hide }) => {
    // set up my state
    const [form, setForm] = React.useState({
        // the nickname
        name: "",
        // the path
        path: "",
    })
    // build the mutation request
    const [request, isInFlight] = useMutation(connectMutation)
    // set up the state update
    const update = (field, value) => {
        // replace my state
        setForm(old => {
            // with
            const clone = {
                // a copy of the old state
                ...old,
                // with the value of the given field replaced with the new one
                [field]: value,
            }
            // update the view
            updateURI(`file:${clone.path}`)
            // hand it off
            return clone
        })
    }
    // set up the archive connector
    const connect = () => {
        // if there is already a pending operation
        if (isInFlight) {
            // skip this update
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                name: `local:${form.name}`,
                uri: `file:${form.path}`,
            },
            // when done
            onCompleted: data => {
                // hide the form
                // hide()
                // and done
                return
            }
        })
    }
    // determine whether i have enough information to make the connection
    const ready = (
        form.name !== null && form.name.length &&
        form.path !== null && form.path.length
    )
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect
    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="local" update={setType} />
                    <Name value={form.name} update={update} />
                    <Path value={form.path} update={update} />
                </Body>
                <Footer>
                </Footer>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={hide}>cancel</Cancel>
        </Panel>
    )
}


// the mutation that connects a local archive
const connectMutation = graphql`
    mutation localArchiveMutation($name: String!, $uri: String!) {
        connectArchive(name: $name, uri: $uri) {
            archive {
                id
                name
                uri
            }
        }
    }
`

// end of file
