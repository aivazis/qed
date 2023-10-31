// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useSetActiveView } from '../explorer/useSetActiveView'
// components
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Name } from './name'
import { Path } from './path'
import { Form, Body, Footer, } from '../form'

// a data archive local to the qed server
export const Local = ({ view, setType, hide }) => {
    // set up my state
    const [form, setForm] = React.useState({
        // the nickname
        name: "",
        // the path
        path: "",
    })
    // get the view mutator
    const decorate = useSetActiveView()
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
            // hand it off
            return clone
        })
        // if the field is the path
        if (field === "path") {
            // update the uri of the archive in the current view
            view.archive.uri = `file:${value}`
            // and set it
            decorate(view)
        }
        // all done
        return
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
            // updater
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("connectArchive")
                // ask for the new archive
                const archive = payload.getLinkedRecord("archive")
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const archives = qed.getLinkedRecords("archives")
                // add the new one to the pile
                qed.setLinkedRecords([...archives, archive], "archives")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // remove the form from the view
                hide()
                // not much to do, for now
                return
            }
        })
    }
    // build a handler that removes the form from view
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
            <Cancel onClick={cancel}>cancel</Cancel>
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
