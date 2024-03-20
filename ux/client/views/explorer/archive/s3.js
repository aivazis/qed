// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useSetActiveView } from '../explorer/useSetActiveView'
// components
import { Busy } from './busy'
import { Panel } from './panel'
import { EnabledConnect, DisabledConnect, Cancel } from './buttons'
import { TypeSelector } from './type'
import { Name } from './name'
import { Profile } from './profile'
import { Region } from './region'
import { Bucket } from './bucket'
import { Path } from './path'
import { Form, Body, Error } from '../form'

// a data archive in an S3 bucket
export const S3 = ({ view, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state
    const [form, setForm] = React.useState({
        // the nickname of the archive; get's used to generate the name of the component
        name: "",
        // the connection profile with the AWS credentials
        profile: "",
        // the AWS region
        region: "",
        // the name of the bucket
        bucket: "",
        // the path
        path: "",
    })
    // get the view mutator
    const decorate = useSetActiveView()
    // build the mutation request
    const [request, isInFlight] = useMutation(connectMutation)
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
        // form the authority portion of the uri
        const authority = (profile.length > 0) ? `${profile}@${region}` : region
        // update the uri of the archive in the current view
        view.archive.uri = `s3://${authority}/${bucket}/${path}`
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
        const profile = form.profile
        const region = form.region
        const bucket = form.bucket
        const path = form.path
        // form the authority portion of the uri
        const authority = profile.length > 0 ? `${profile}@${region}` : region
        // update the uri of the archive in the current view
        const uri = `s3://${authority}/${bucket}/${path}`
        // send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                name: `s3:${form.name}`,
                uri,
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
                setError(error)
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
    const ready = (!isInFlight && (form.name !== null) && (form.name.length))
    // use this to figure out which button to render
    const Connect = ready ? EnabledConnect : DisabledConnect
    // render
    return (
        <Panel>
            <Form>
                <Body>
                    <TypeSelector value="s3" update={setType} />
                    <Name value={form.name} update={update} />
                    <Profile value={form.profile} update={update} />
                    <Region value={form.region} update={update} />
                    <Bucket value={form.bucket} update={update} />
                    <Path value={form.path} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            {!isInFlight && <Cancel onClick={cancel}>cancel</Cancel>}
            {error && <Error>{error}</Error>}
            {isInFlight && <Busy />}
        </Panel>
    )
}


// the mutation that connects a archive
const connectMutation = graphql`
    mutation s3ArchiveMutation($name: String!, $uri: String!) {
        connectArchive(name: $name, uri: $uri) {
            archive {
                id
                name
                uri
                readers
            }
        }
    }
`


// end of file
