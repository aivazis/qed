// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useSetActiveView } from '../explorer/useSetActiveView'
// the store updater the archive mutations share
import { connectArchiveUpdater, reconfigureArchiveUpdater } from '../archives/archiveListUpdaters'
// components
import { Busy } from './busy'
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Name } from './name'
import { useFetchArchiveNickname } from './useFetchArchiveNickname'
import { Path } from './path'
import { Form, Body, Error } from '../form'

// a data archive local to the qed server; the form connects a new one, or reconfigures {edit}
export const Local = ({ view, edit = null, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state, from what the archive being reconfigured says about itself, if any
    const [form, setForm] = React.useState({
        // the nickname, which is the name of the archive without its kind
        name: edit === null ? "" : edit.name.replace(/^local:/, ""),
        // the path, which is its location without the scheme
        path: edit === null ? "" : edit.uri.replace(/^file:/, ""),
    })
    // get the view mutator
    const decorate = useSetActiveView()
    // build the mutation request: a new archive gets connected, an existing one reconfigured
    const [request, isInFlight] = useMutation(
        edit === null ? localArchiveMutation : localArchiveReconfigureMutation
    )
    // ask the server for a nickname for a new archive, once the form names a folder
    const suggestion = useFetchArchiveNickname({
        // of my kind
        type: "local",
        // at the location the form describes
        uri: form.path ? `file:${form.path}` : "",
        // an archive that exists already keeps its name
        skip: edit !== null,
    })
    // set up the state update
    const update = (field, value) => {
        // clear any errors
        setError(null)
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
        // otherwise, collect the current state
        const name = form.name || suggestion
        const path = form.path
        // the location of the archive
        const uri = `file:${path}`
        // which needs no settings to get at
        const credentials = { tokens: [] }
        // a new archive is connected under its name, an existing one is moved to the new location
        const input = (edit === null)
            ? { name: `local:${name}`, uri, credentials }
            : { uri: edit.uri, location: uri, credentials }
        // send the mutation to the server
        request({
            // input
            variables: { input },
            // updater: a new archive joins the pile, an existing one takes its own old place
            updater: (edit === null)
                ? connectArchiveUpdater("connectArchive")
                : reconfigureArchiveUpdater(edit.uri),
            // when done
            onCompleted: data => {
                // clear the error
                setError(null)
                // remove the form from the view
                hide()
                // all done
                return
            },
            // if something went wrong
            onError: error => {
                // record the error
                setError([
                    `got: ${error}`,
                    `while ${edit === null ? "connecting" : "reconfiguring"} the data archive '${name}'`,
                    `at '${path}'`,
                ])
                // all done
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
        hide()
        // all done
        return
    }
    // determine whether i have enough information to make the connection
    const ready = (
        !isInFlight &&
        (form.name || suggestion).length > 0 &&
        form.path !== null && form.path.length > 0
    )
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect
    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="local" update={setType} />
                    <Path value={form.path} update={update} />
                    <Name value={form.name} suggestion={suggestion} update={update}
                        fixed={edit !== null} />
                </Body>
            </Form>
            <Connect connect={connect} label={edit === null ? "connect" : "update"} />
            {!isInFlight && <Cancel onClick={cancel}>cancel</Cancel>}
            {error && <Error errors={error} />}
            {isInFlight && <Busy />}
        </Panel>
    )
}


// the mutation that connects a local archive
export const localArchiveMutation = graphql`
    mutation localArchiveMutation($input: ConnectArchiveInput!) {
        connectArchive(input: $input) {
            archive {
                id
                name
                type
                uri
                credentials {
                    name
                    value
                }
                readers
                expanded
                pending
                error
                hits
                dirty
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`


// the mutation that points an archive at a new location
export const localArchiveReconfigureMutation = graphql`
    mutation localArchiveReconfigureMutation($input: ReconfigureArchiveInput!) {
        reconfigureArchive(input: $input) {
            archive {
                id
                name
                type
                uri
                credentials {
                    name
                    value
                }
                readers
                expanded
                pending
                error
                hits
                dirty
                items {
                    id
                    name
                    uri
                    isFolder
                    parent
                    expanded
                    pending
                    error
                }
            }
        }
    }
`


// end of file
