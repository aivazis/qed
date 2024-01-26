// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'

// local
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Type } from './type'
import { Name } from './name'
import { Shape } from './shape'
import { Form, Body, Field, Values, Error, enumValue } from '../form'


// associate a native reader with a given data product
export const Native = ({ view, setType, hide }) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // set up my state
    const [form, setForm] = React.useState({
        // the pyre name of the reader
        name: "",
        // its shape
        lines: "",
        samples: "",
        // and data type
        cell: ""
    })
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
                spec: {
                    reader: "native.flat",
                    name: form.name,
                    uri: view.reader.uri,
                    lines: form.lines,
                    samples: form.samples,
                    cell: form.cell,
                }
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
                // clear the error
                setError(null)
                // remove the form from view
                hide()
                // all done
                return
            },
            // if something went wrong
            onError: error => {
                // clear the form
                update("lines", "")
                update("samples", "")
                update("cell", "")
                // and now record the error
                setError(error)
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
        form.name !== null && form.name.length &&
        form.cell !== null && form.cell.length
    )
    // figure out the state of the connect button
    const Connect = ready ? EnabledConnect : DisabledConnect
    // and render
    return (
        <Panel>
            <Form>
                <Body>
                    <Type value="native" update={setType} />
                    <Name value={form.name} update={update} />
                    <Shape lines={form.lines} samples={form.samples} update={update} />
                    <Cells value={form.cell} update={update} />
                </Body>
            </Form>
            <Connect connect={connect} />
            <Cancel onClick={cancel}>cancel</Cancel>
            {error && <Error>{error}</Error>}
        </Panel>
    )
}


// the data type selector
export const Cells = ({ value, update }) => {
    // make a handler that sets the reader type
    const select = type => {
        // build the selector
        return () => {
            // update the form state
            update("cell", type)
            // all done
            return
        }
    }
    // render
    return (
        <Field name="data type" value={value} tip="select the reader type">
            <Values>
                <Cell name="char" rep="char" current={value} select={select} />
                <Cell name="int16" rep="int16" current={value} select={select} />
                <Cell name="int32" rep="int32" current={value} select={select} />
                <Cell name="int64" rep="int64" current={value} select={select} />
                <Cell name="real32" rep="real32" current={value} select={select} />
                <Cell name="real64" rep="real64" current={value} select={select} />
                <Cell name="complex64" rep="complex64" current={value} select={select} />
                <Cell name="complex128" rep="complex128" current={value} select={select} />
            </Values>
        </Field>
    )
}


// the product type field
const Cell = ({ name, rep, current, select }) => {
    // assemble the behaviors
    const behaviors = {
        onClick: select(rep)
    }
    // deduce my state
    const state = current === rep ? "selected" : "enabled"
    // pick a field selector based on my state
    const Selector = enumValue(state)
    // and render it
    return (
        <Selector {...behaviors}>
            {name}
        </Selector>
    )
}


// the mutation that associates a Native reader with a data product
const connectMutation = graphql`
    mutation nativeReaderMutation($spec: ReaderInput!) {
        connectReader(spec: $spec) {
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
