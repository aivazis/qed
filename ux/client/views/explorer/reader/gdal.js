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
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Type } from './type'
import { Name } from './name'
import { Form, Body, Field, Values, enumValue } from '../form'


// associate a GDAL reader with a given data product
export const GDAL = ({ view, setType, hide }) => {
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
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
            // hand it off
            return clone
        })
        // all done
        return
    }
    // set up the reader connector
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
                reader: "native.gdal",
                name: form.name,
                uri: view.reader.uri,
            },
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("connectReader")
                // ask for the new reader
                const reader = payload.getLinkedRecord("reader")
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const readers = qed.getLinkedRecords("readers")
                // add the new one to the pile
                qed.setLinkedRecords([...readers, reader], "readers")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // remove the form from view
                hide()
                // all done
                return
            }
        })
    }
    // build the handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effect
        evt.preventDefault()
        // remove the view in my viewport from the pile
        hide()
        // all done
        return
    }
    // determine whether i have enough information to make the connection
    const ready = (
        form.name !== null && form.name.length
    )
    // figure out the state of the connect button
    const Connect = ready ? EnabledConnect : DisabledConnect
    // and render
    return (
        <Panel>
            <Form>
                <Body>
                    <Type value="gdal" update={setType} />
                    <Name value={form.name} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
        </Panel>
    )
}


// the mutation that associates a GDAL reader with a data product
const connectMutation = graphql`
    mutation gdalReaderMutation($reader: String!, $name: String!, $uri: String!) {
        connectReader(reader: $reader, name: $name, uri: $uri) {
            reader {
                id
                name
                uri
                api
                selectors {
                    name
                    values
                }
                datasets {
                    name
                    datatype
                    selector {
                        name
                        value
                    }
                    channels
                    shape
                    origin
                    tile
                }
            }
        }
    }
`


// end of file
