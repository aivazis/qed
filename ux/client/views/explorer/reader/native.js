// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useConnectReader } from './useConnectReader'
// components
import { Panel } from './panel'
import { Cancel, DisabledConnect, EnabledConnect } from './buttons'
import { Name } from './name'
import { Product } from './product'
import { Shape } from './shape'
import { Type } from './type'
import { Form, Body, Field, Values, Error } from '../form'


// associate a native reader with a given data product
export const Native = ({ view, setType, hide }) => {
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
    // get the reader connection support
    const { error, update, makeConnector, cancel } = useConnectReader(setForm, hide)
    // build the payload
    const spec = {
        reader: "native.flat",
        name: form.name,
        uri: view.reader.uri,
        lines: form.lines,
        samples: form.samples,
        cell: form.cell,
    }
    // use it to build the connector
    const connect = makeConnector(spec)
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
                <Product name="char" rep="char" current={value} select={select} />
                <Product name="int16" rep="int16" current={value} select={select} />
                <Product name="int32" rep="int32" current={value} select={select} />
                <Product name="int64" rep="int64" current={value} select={select} />
                <Product name="real32" rep="real32" current={value} select={select} />
                <Product name="real64" rep="real64" current={value} select={select} />
                <Product name="complex64" rep="complex64" current={value} select={select} />
                <Product name="complex128" rep="complex128" current={value} select={select} />
            </Values>
        </Field>
    )
}


// end of file
