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
import { connectArchiveUpdater, reconfigureArchiveUpdater } from '../archives/archiveListUpdaters'
// components
import { Busy } from './busy'
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Name } from './name'
import { useFetchArchiveNickname } from './useFetchArchiveNickname'
import { Profile } from './profile'
import { Region } from './region'
import { Bucket } from './bucket'
import { Path } from './path'
import { Form, Body, Error } from '../form'

// a data archive in an S3 bucket; the form connects a new one, or reconfigures {edit}
export const S3 = ({ view, edit = null, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state, from what the archive being reconfigured says about itself, if any
    const [form, setForm] = React.useState(() => describe(edit))
    // get the view mutator
    const decorate = useSetActiveView()
    // build the mutation request: a new archive gets connected, an existing one reconfigured
    const [request, isInFlight] = useMutation(edit === null ? connectMutation : reconfigureMutation)
    // ask the server for a nickname for a new archive, once the form names a bucket
    const suggestion = useFetchArchiveNickname({
        // of my kind
        type: "s3",
        // at the location the form describes
        uri: form.bucket ? `s3://${form.bucket}/${form.path}` : "",
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
        // collect the current state
        const profile = (field == "profile") ? value : form.profile
        const region = (field == "region") ? value : form.region
        const bucket = (field == "bucket") ? value : form.bucket
        const path = (field == "path") ? value : form.path
        // update the uri of the archive in the current view
        view.archive.uri = `s3://${bucket}/${path}`
        // and set it
        decorate(view)
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
        const profile = form.profile
        const region = form.region
        const bucket = form.bucket
        const path = form.path
        // update the uri of the archive in the current view
        const uri = `s3://${bucket}/${path}`
        // the settings that say how to get at it
        const credentials = {
            tokens: [
                { name: "profile", value: profile },
                { name: "region", value: region },
            ]
        }
        // a new archive is connected under its name, an existing one is moved to the new location
        const input = (edit === null)
            ? { name: `s3:${name}`, uri, credentials }
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
                    `at '${uri}'`,
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
    const ready = (!isInFlight && (form.name || suggestion).length > 0)
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect
    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="s3" update={setType} />
                    <Name value={form.name} suggestion={suggestion} update={update}
                        fixed={edit !== null} />
                    <Profile value={form.profile} update={update} />
                    <Region value={form.region} update={update} />
                    <Bucket value={form.bucket} update={update} />
                    <Path value={form.path} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} label={edit === null ? "connect" : "update"} />
            {!isInFlight && <Cancel onClick={cancel}>cancel</Cancel>}
            {error && <Error errors={error} />}
            {isInFlight && <Busy />}
        </Panel>
    )
}


// the mutation that connects a archive
const connectMutation = graphql`
    mutation s3ArchiveMutation($input: ConnectArchiveInput!) {
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


// the state of the form that describes {archive}, or of a blank one when there is no archive
const describe = archive => {
    // with no archive
    if (archive === null) {
        // the form starts out blank
        return {
            // the nickname of the archive; gets used to generate the name of the component
            name: "",
            // the connection profile with the AWS credentials
            profile: "",
            // the AWS region
            region: "",
            // the name of the bucket
            bucket: "",
            // the path
            path: "",
        }
    }
    // the settings of the archive, by name
    const settings = Object.fromEntries(archive.credentials.map(({ name, value }) => [name, value]))
    // its location, without the scheme
    const location = archive.uri.replace(/^s3:\/\//, "")
    // the bucket ends at the first slash
    const slash = location.indexOf("/")
    // fill the form
    return {
        // with the nickname, which is the name of the archive without its kind
        name: archive.name.replace(/^s3:/, ""),
        // the profile
        profile: settings.profile ?? "",
        // the region
        region: settings.region ?? "",
        // the bucket
        bucket: slash === -1 ? location : location.slice(0, slash),
        // and the path within it
        path: slash === -1 ? "" : location.slice(slash + 1),
    }
}


const reconfigureMutation = graphql`
    mutation s3ArchiveReconfigureMutation($input: ReconfigureArchiveInput!) {
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
